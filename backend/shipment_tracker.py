import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from weather_monitor import get_port_weather, MONITORED_LOCATIONS
from knowledge_base import search_similar_disruptions

load_dotenv()

# Major shipping routes and which ports/chokepoints they pass through
SHIPPING_ROUTES = {
    "Asia-Europe": {
        "description": "Asia to Europe via Suez Canal",
        "chokepoints": ["Strait of Malacca", "Suez Canal", "Bab el Mandeb", "Red Sea"],
        "ports": ["Port of Shanghai", "Port of Singapore", "Port of Rotterdam", "Port of Antwerp", "Port of Hamburg"],
        "avg_transit_days": 25,
        "alternate_route": "Asia-Europe-Cape",
        "alternate_extra_days": 14
    },
    "Asia-Europe-Cape": {
        "description": "Asia to Europe via Cape of Good Hope",
        "chokepoints": ["Strait of Malacca"],
        "ports": ["Port of Shanghai", "Port of Singapore", "Port of Rotterdam"],
        "avg_transit_days": 39,
        "alternate_route": None,
        "alternate_extra_days": 0
    },
    "Asia-Americas-West": {
        "description": "Asia to West Coast Americas via Pacific",
        "chokepoints": ["Taiwan Strait"],
        "ports": ["Port of Shanghai", "Port of Busan", "Port of Los Angeles", "Port of Long Beach"],
        "avg_transit_days": 14,
        "alternate_route": "Asia-Americas-Panama",
        "alternate_extra_days": 10
    },
    "Asia-Americas-East": {
        "description": "Asia to East Coast Americas via Panama Canal",
        "chokepoints": ["Panama Canal", "Taiwan Strait"],
        "ports": ["Port of Shanghai", "Port of Busan", "Port of New York", "Port of Houston"],
        "avg_transit_days": 28,
        "alternate_route": "Asia-Americas-Cape",
        "alternate_extra_days": 18
    },
    "Asia-Americas-Panama": {
        "description": "Asia to Americas via Panama Canal",
        "chokepoints": ["Panama Canal"],
        "ports": ["Port of Shanghai", "Port of Los Angeles", "Port of New York"],
        "avg_transit_days": 24,
        "alternate_route": None,
        "alternate_extra_days": 0
    },
    "Europe-Americas": {
        "description": "Europe to Americas via Atlantic",
        "chokepoints": ["Dover Strait", "English Channel"],
        "ports": ["Port of Rotterdam", "Port of Hamburg", "Port of New York", "Port of Houston"],
        "avg_transit_days": 10,
        "alternate_route": None,
        "alternate_extra_days": 0
    },
    "Middle-East-Asia": {
        "description": "Middle East to Asia via Arabian Sea",
        "chokepoints": ["Strait of Hormuz", "Bab el Mandeb"],
        "ports": ["Port of Mumbai", "Port of Singapore", "Port of Shanghai"],
        "avg_transit_days": 12,
        "alternate_route": None,
        "alternate_extra_days": 0
    },
    "Intra-Asia": {
        "description": "Within Asia Pacific",
        "chokepoints": ["Strait of Malacca", "Taiwan Strait"],
        "ports": ["Port of Shanghai", "Port of Singapore", "Port of Busan", "Port of Hong Kong", "Port of Tokyo"],
        "avg_transit_days": 5,
        "alternate_route": None,
        "alternate_extra_days": 0
    },
    "Domestic-India": {
    "description": "Domestic India land or air route",
    "chokepoints": [],
    "ports": [],
    "avg_transit_days": 3,
    "alternate_route": None,
    "alternate_extra_days": 0
},
}

# Port to region mapping for route detection
PORT_REGIONS = {
    # Asia ports
    "shanghai": "Asia", "china": "Asia", "beijing": "Asia",
    "singapore": "Asia", "hong kong": "Asia", "busan": "Asia",
    "korea": "Asia", "japan": "Asia", "tokyo": "Asia",
    "mumbai": "Asia", "india": "Asia", "ningbo": "Asia",
    "shenzhen": "Asia", "guangzhou": "Asia", "klang": "Asia",
    "malaysia": "Asia", "vietnam": "Asia", "bangkok": "Asia",
    "taiwan": "Asia", "indonesia": "Asia",

    # Europe ports
    "rotterdam": "Europe", "netherlands": "Europe",
    "antwerp": "Europe", "belgium": "Europe",
    "hamburg": "Europe", "germany": "Europe",
    "felixstowe": "Europe", "uk": "Europe", "london": "Europe",
    "barcelona": "Europe", "spain": "Europe",
    "france": "Europe", "italy": "Europe",

    # Americas ports
    "los angeles": "Americas", "long beach": "Americas",
    "new york": "Americas", "houston": "Americas",
    "usa": "Americas", "america": "Americas",
    "santos": "Americas", "brazil": "Americas",
    "canada": "Americas", "mexico": "Americas",

    # Middle East
    "dubai": "Middle-East", "uae": "Middle-East",
    "saudi": "Middle-East", "qatar": "Middle-East",
    "oman": "Middle-East", "kuwait": "Middle-East",
}


def detect_route(origin: str, destination: str) -> str:
    origin_lower = origin.lower()
    destination_lower = destination.lower()

    # Indian cities and keywords
    india_keywords = [
        "india", "mumbai", "delhi", "bangalore", "chennai",
        "kolkata", "hyderabad", "pune", "ahmedabad", "jaipur",
        "surat", "lucknow", "kanpur", "nagpur", "bhopal",
        "indore", "patna", "vadodara", "goa", "kochi"
    ]

    origin_is_india = any(k in origin_lower for k in india_keywords)
    destination_is_india = any(k in destination_lower for k in india_keywords)

    # If both are in India — domestic route, no sea involved
    if origin_is_india and destination_is_india:
        print(f"Detected domestic India route: {origin} -> {destination}")
        return "Domestic-India"

    # Find regions for international routes
    origin_region = "Unknown"
    destination_region = "Unknown"

    for keyword, region in PORT_REGIONS.items():
        if keyword in origin_lower:
            origin_region = region
        if keyword in destination_lower:
            destination_region = region

    # Map region pairs to routes
    route_map = {
        ("Asia", "Europe"): "Asia-Europe",
        ("Europe", "Asia"): "Asia-Europe",
        ("Asia", "Americas"): "Asia-Americas-West",
        ("Americas", "Asia"): "Asia-Americas-West",
        ("Europe", "Americas"): "Europe-Americas",
        ("Americas", "Europe"): "Europe-Americas",
        ("Middle-East", "Asia"): "Middle-East-Asia",
        ("Asia", "Middle-East"): "Middle-East-Asia",
        ("Asia", "Asia"): "Intra-Asia",
    }

    route_key = (origin_region, destination_region)
    detected_route = route_map.get(route_key, "Asia-Europe")

    print(f"Detected route: {origin} ({origin_region}) -> {destination} ({destination_region})")
    print(f"Using route: {detected_route}")

    return detected_route


def check_route_risks(route_name: str) -> dict:
    """
    Checks all weather and news risks along a specific route
    Returns risk summary for the route
    """
    route = SHIPPING_ROUTES.get(route_name, SHIPPING_ROUTES["Asia-Europe"])

    weather_risks = []
    affected_chokepoints = []
    affected_ports = []

    # Check weather at all chokepoints on this route
    print(f"\nChecking weather at {len(route['chokepoints'])} chokepoints...")
    for chokepoint in route["chokepoints"]:
        location = next(
            (loc for loc in MONITORED_LOCATIONS if loc["name"] == chokepoint),
            None
        )
        if location:
            weather = get_port_weather(location)
            if weather and weather["current_risk"] in ["Medium", "High", "Critical"]:
                weather_risks.append(weather)
                affected_chokepoints.append(chokepoint)

    # Check weather at key ports on this route
    print(f"Checking weather at {len(route['ports'])} ports...")
    for port in route["ports"]:
        location = next(
            (loc for loc in MONITORED_LOCATIONS if loc["name"] == port),
            None
        )
        if location:
            weather = get_port_weather(location)
            if weather and weather["current_risk"] in ["High", "Critical"]:
                weather_risks.append(weather)
                affected_ports.append(port)

    # Search historical context
    search_query = f"shipping disruption {route_name} {' '.join(route['chokepoints'])}"
    historical = search_similar_disruptions(search_query, k=2)

    return {
        "route_name": route_name,
        "route_description": route["description"],
        "weather_risks": weather_risks,
        "affected_chokepoints": affected_chokepoints,
        "affected_ports": affected_ports,
        "historical_context": historical,
        "avg_transit_days": route["avg_transit_days"],
        "alternate_route": route["alternate_route"],
        "alternate_extra_days": route["alternate_extra_days"]
    }


def estimate_delay(route_risks: dict) -> dict:
    """
    Estimates shipment delay based on active risks
    Uses historical data from ChromaDB for accuracy
    """
    # Domestic routes have no maritime risks
    if route_risks["route_name"] == "Domestic-India":
        return {
            "estimated_delay_days": 0,
            "delay_reasons": [],
            "confidence": "High"
        }

    base_delay = 0
    delay_reasons = []

    # Weather based delays
    for risk in route_risks["weather_risks"]:
        if risk["current_risk"] == "Critical":
            base_delay += 5
            delay_reasons.append(f"Critical weather at {risk['location']} (+5 days)")
        elif risk["current_risk"] == "High":
            base_delay += 3
            delay_reasons.append(f"High weather risk at {risk['location']} (+3 days)")
        elif risk["current_risk"] == "Medium":
            base_delay += 1
            delay_reasons.append(f"Moderate weather at {risk['location']} (+1 day)")

    # Historical context based delays
    for doc in route_risks["historical_context"]:
        content = doc.page_content.lower()
        if "critical" in content or "blocked" in content:
            base_delay += 3
            delay_reasons.append("Historical critical disruption on similar route (+3 days)")
            break
        elif "high" in content or "significant" in content:
            base_delay += 1
            delay_reasons.append("Historical disruption pattern on route (+1 day)")
            break

    return {
        "estimated_delay_days": base_delay,
        "delay_reasons": delay_reasons,
        "confidence": "High" if len(delay_reasons) > 0 else "Low"
    }


def track_shipment(origin: str, destination: str, expected_delivery: str) -> dict:
    """
    Main function — tracks a shipment and estimates delays
    """
    print(f"\n{'='*50}")
    print(f"TRACKING SHIPMENT")
    print(f"{'='*50}")
    print(f"Origin: {origin}")
    print(f"Destination: {destination}")
    print(f"Expected Delivery: {expected_delivery}")

    # Detect route
    route_name = detect_route(origin, destination)

    # Check risks on route
    route_risks = check_route_risks(route_name)

    # Estimate delay
    delay_estimate = estimate_delay(route_risks)

    # Calculate new delivery date
    try:
        original_date = datetime.strptime(expected_delivery, "%Y-%m-%d")
        new_date = original_date + timedelta(days=delay_estimate["estimated_delay_days"])
        new_delivery = new_date.strftime("%Y-%m-%d")
    except:
        new_delivery = "Unable to calculate"

    # Build result
    result = {
        "origin": origin,
        "destination": destination,
        "route": route_name,
        "route_description": route_risks["route_description"],
        "original_delivery": expected_delivery,
        "estimated_delay_days": delay_estimate["estimated_delay_days"],
        "revised_delivery": new_delivery,
        "delay_reasons": delay_estimate["delay_reasons"],
        "affected_chokepoints": route_risks["affected_chokepoints"],
        "affected_ports": route_risks["affected_ports"],
        "weather_risks": route_risks["weather_risks"],
        "alternate_route": route_risks["alternate_route"],
        "alternate_extra_days": route_risks["alternate_extra_days"],
        "confidence": delay_estimate["confidence"]
    }

    return result


if __name__ == "__main__":
    # Test with sample shipments
    test_shipments = [
        {
            "origin": "Shanghai, China",
            "destination": "Rotterdam, Netherlands",
            "expected_delivery": "2026-07-25"
        },
        {
            "origin": "Singapore",
            "destination": "Los Angeles, USA",
            "expected_delivery": "2026-07-30"
        },
        {
            "origin": "Mumbai, India",
            "destination": "Dubai, UAE",
            "expected_delivery": "2026-07-20"
        }
    ]

    for shipment in test_shipments:
        result = track_shipment(
            shipment["origin"],
            shipment["destination"],
            shipment["expected_delivery"]
        )

        print(f"\n{'='*50}")
        print("SHIPMENT RISK ADVISORY")
        print(f"{'='*50}")
        print(f"Route: {result['route_description']}")
        print(f"Planned Delivery: {result['original_delivery']}")
        print(f"Risk Assessment: {result['estimated_delay_days']} day delay likely")
        print(f"Advised Delivery: {result['revised_delivery']}")

        if result['delay_reasons']:
            print(f"\nDelay Reasons:")
            for reason in result['delay_reasons']:
                print(f"  → {reason}")

        if result['affected_chokepoints']:
            print(f"\nAffected Chokepoints: {', '.join(result['affected_chokepoints'])}")

        if result['alternate_route'] and result['estimated_delay_days'] > 2:
            print(f"\n⚠️  RISK ADVISORY:")
            print(f"If you have a shipment on this route right now —")
            print(f"Consider alternate route: {result['alternate_route']}")
            print(f"Extra transit time: +{result['alternate_extra_days']} days")
            print(f"Benefit: Avoids current disruptions on primary route")

        print(f"\nConfidence: {result['confidence']}")
        print("-"*50)