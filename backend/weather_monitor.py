import os
import requests
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# All 30 monitored locations
MONITORED_LOCATIONS = [
    # Asia
    {"name": "Port of Shanghai", "lat": 31.2304, "lon": 121.4737, "region": "Asia"},
    {"name": "Port of Singapore", "lat": 1.2644, "lon": 103.8223, "region": "Asia"},
    {"name": "Port of Ningbo", "lat": 29.8683, "lon": 121.5440, "region": "Asia"},
    {"name": "Port of Shenzhen", "lat": 22.5431, "lon": 114.0579, "region": "Asia"},
    {"name": "Port of Guangzhou", "lat": 23.1291, "lon": 113.2644, "region": "Asia"},
    {"name": "Port of Busan", "lat": 35.1796, "lon": 129.0756, "region": "Asia"},
    {"name": "Port of Hong Kong", "lat": 22.3193, "lon": 114.1694, "region": "Asia"},
    {"name": "Port of Klang", "lat": 3.0319, "lon": 101.3903, "region": "Asia"},
    {"name": "Port of Tokyo", "lat": 35.6762, "lon": 139.6503, "region": "Asia"},
    {"name": "Port of Mumbai", "lat": 18.9322, "lon": 72.8264, "region": "Asia"},

    # Europe
    {"name": "Port of Rotterdam", "lat": 51.9225, "lon": 4.4792, "region": "Europe"},
    {"name": "Port of Antwerp", "lat": 51.2194, "lon": 4.4025, "region": "Europe"},
    {"name": "Port of Hamburg", "lat": 53.5753, "lon": 10.0153, "region": "Europe"},
    {"name": "Port of Felixstowe", "lat": 51.9639, "lon": 1.3514, "region": "Europe"},
    {"name": "Port of Barcelona", "lat": 41.3851, "lon": 2.1734, "region": "Europe"},

    # Americas
    {"name": "Port of Los Angeles", "lat": 33.7361, "lon": -118.2639, "region": "Americas"},
    {"name": "Port of Long Beach", "lat": 33.7701, "lon": -118.1937, "region": "Americas"},
    {"name": "Port of New York", "lat": 40.6892, "lon": -74.0445, "region": "Americas"},
    {"name": "Port of Houston", "lat": 29.7604, "lon": -95.3698, "region": "Americas"},
    {"name": "Port of Santos", "lat": -23.9618, "lon": -46.3322, "region": "Americas"},

    # Critical Chokepoints
    {"name": "Suez Canal", "lat": 30.5852, "lon": 32.2654, "region": "Chokepoint"},
    {"name": "Strait of Malacca", "lat": 1.2655, "lon": 103.8196, "region": "Chokepoint"},
    {"name": "Panama Canal", "lat": 9.0801, "lon": -79.6845, "region": "Chokepoint"},
    {"name": "Strait of Hormuz", "lat": 26.5667, "lon": 56.2500, "region": "Chokepoint"},
    {"name": "Bab el Mandeb", "lat": 12.5833, "lon": 43.3333, "region": "Chokepoint"},
    {"name": "Taiwan Strait", "lat": 24.0000, "lon": 119.5000, "region": "Chokepoint"},
    {"name": "Dover Strait", "lat": 51.1000, "lon": 1.4000, "region": "Chokepoint"},
    {"name": "Red Sea", "lat": 20.0, "lon": 38.0, "region": "Chokepoint"},
    {"name": "Black Sea", "lat": 43.0000, "lon": 34.0000, "region": "Chokepoint"},
    {"name": "English Channel", "lat": 50.5000, "lon": -1.0000, "region": "Chokepoint"},
]

# Risk thresholds
def classify_weather_risk(wind_kph, visibility_km, condition_text):
    """
    Classifies weather risk level based on conditions
    """
    condition_lower = condition_text.lower()

    # Critical conditions
    if (wind_kph > 80 or
        "hurricane" in condition_lower or
        "typhoon" in condition_lower or
        "tornado" in condition_lower):
        return "Critical"

    # High conditions
    if (wind_kph > 50 or
        visibility_km < 1 or
        "storm" in condition_lower or
        "blizzard" in condition_lower or
        "heavy snow" in condition_lower):
        return "High"

    # Medium conditions
    if (wind_kph > 30 or
        visibility_km < 3 or
        "fog" in condition_lower or
        "heavy rain" in condition_lower or
        "thunderstorm" in condition_lower):
        return "Medium"

    return "Low"


def get_port_weather(location):
    """
    Fetches current weather and 3 day forecast
    for a specific port or chokepoint
    """
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": f"{location['lat']},{location['lon']}",
        "days": 3,
        "aqi": "no",
        "alerts": "yes"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        forecast = data["forecast"]["forecastday"]

        wind_kph = current["wind_kph"]
        visibility_km = current["vis_km"]
        condition = current["condition"]["text"]
        temp_c = current["temp_c"]

        # Classify current risk
        risk_level = classify_weather_risk(
            wind_kph, visibility_km, condition
        )

        # Check forecast for upcoming risks
        upcoming_risks = []
        for day in forecast:
            for hour in day["hour"]:
                hour_wind = hour["wind_kph"]
                hour_vis = hour["vis_km"]
                hour_condition = hour["condition"]["text"]
                hour_risk = classify_weather_risk(
                    hour_wind, hour_vis, hour_condition
                )
                if hour_risk in ["High", "Critical"]:
                    upcoming_risks.append({
                        "time": hour["time"],
                        "risk": hour_risk,
                        "wind_kph": hour_wind,
                        "condition": hour_condition
                    })

        return {
            "location": location["name"],
            "region": location["region"],
            "current_risk": risk_level,
            "wind_kph": wind_kph,
            "visibility_km": visibility_km,
            "condition": condition,
            "temp_c": temp_c,
            "upcoming_risks": upcoming_risks[:3],
            "has_alerts": len(data.get("alerts", {}).get("alert", [])) > 0,
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather for {location['name']}: {e}")
        return None


def monitor_all_ports():
    """
    Checks weather for all 30 monitored locations in parallel
    Much faster than sequential checking
    """
    print(f"Checking weather at {len(MONITORED_LOCATIONS)} locations in parallel...\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(get_port_weather, MONITORED_LOCATIONS))

    all_results = [r for r in results if r is not None]
    risk_alerts = [r for r in all_results if r["current_risk"] in ["Medium", "High", "Critical"]]

    print(f"Checked {len(all_results)} locations successfully")
    print(f"Found {len(risk_alerts)} locations with elevated weather risk\n")

    return all_results, risk_alerts


def get_weather_summary():
    """
    Main function — returns weather risk summary
    for dashboard display
    """
    all_results, risk_alerts = monitor_all_ports()

    summary = {
        "total_monitored": len(all_results),
        "risk_locations": len(risk_alerts),
        "critical": [r for r in risk_alerts if r["current_risk"] == "Critical"],
        "high": [r for r in risk_alerts if r["current_risk"] == "High"],
        "medium": [r for r in risk_alerts if r["current_risk"] == "Medium"],
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return summary, risk_alerts


if __name__ == "__main__":
    print("="*50)
    print("WEATHER RISK MONITOR")
    print("="*50)
    print(f"Monitoring {len(MONITORED_LOCATIONS)} ports and chokepoints\n")

    summary, risk_alerts = get_weather_summary()

    print(f"\n{'='*50}")
    print("WEATHER RISK SUMMARY")
    print(f"{'='*50}")
    print(f"Total locations monitored: {summary['total_monitored']}")
    print(f"Locations with elevated risk: {summary['risk_locations']}")
    print(f"Critical: {len(summary['critical'])}")
    print(f"High: {len(summary['high'])}")
    print(f"Medium: {len(summary['medium'])}")

    if risk_alerts:
        print(f"\n{'='*50}")
        print("WEATHER RISK ALERTS")
        print(f"{'='*50}")
        for alert in risk_alerts:
            print(f"\n📍 {alert['location']} ({alert['region']})")
            print(f"   Risk Level: {alert['current_risk']}")
            print(f"   Condition: {alert['condition']}")
            print(f"   Wind Speed: {alert['wind_kph']} km/h")
            print(f"   Visibility: {alert['visibility_km']} km")
            if alert['upcoming_risks']:
                print(f"   Upcoming High Risk Periods: {len(alert['upcoming_risks'])}")
                for ur in alert['upcoming_risks'][:2]:
                    print(f"   → {ur['time']}: {ur['risk']} ({ur['condition']}, {ur['wind_kph']}km/h wind)")
    else:
        print("\n✅ No elevated weather risks detected at any monitored location")

    print(f"\nLast checked: {summary['checked_at']}")