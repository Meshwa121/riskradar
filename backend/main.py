import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from news_ingestion import get_filtered_articles
from risk_analyzer import analyze_article
from weather_monitor import get_weather_summary
from shipment_tracker import track_shipment

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="RiskRadar API",
    description="Agentic Supply Chain Risk Detection Platform",
    version="1.0.0"
)

# Allow React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────
class ShipmentRequest(BaseModel):
    origin: str
    destination: str
    expected_delivery: str

class QueryRequest(BaseModel):
    question: str

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "RiskRadar API is running",
        "version": "1.0.0",
        "endpoints": [
            "/risks",
            "/weather",
            "/shipment",
            "/health"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "All systems operational"}

@app.get("/risks")
async def get_risks():
    try:
        print("Fetching live news articles...")
        articles = get_filtered_articles()

        if not articles:
            return {"risks": [], "message": "No articles found"}

        print(f"Analyzing {min(3, len(articles))} articles...")
        risks = []

        for article in articles[:3]:
            try:
                result = analyze_article(article)
                if result:
                    risks.append(result)
            except Exception as e:
                print(f"Error analyzing article: {e}")
                continue

        return {
            "total": len(risks),
            "risks": risks
        }

    except Exception as e:
        print(f"Error in /risks endpoint: {e}")
        return {"risks": [], "message": str(e)}


@app.get("/weather")
async def get_weather():
    try:
        print("Checking weather at all monitored locations...")
        summary, risk_alerts = get_weather_summary()
        
        # Also get all locations for full page view
        from weather_monitor import monitor_all_ports
        all_results, _ = monitor_all_ports()

        return {
            "summary": {**summary, "all_locations": all_results},
            "alerts": risk_alerts
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/shipment")
async def analyze_shipment(request: ShipmentRequest):
    """
    Analyzes risks for a specific shipment route
    Returns delay estimate and risk advisory
    """
    try:
        print(f"Analyzing shipment: {request.origin} → {request.destination}")
        result = track_shipment(
            request.origin,
            request.destination,
            request.expected_delivery
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/routes")
async def get_routes():
    """
    Returns list of all monitored shipping routes
    """
    from shipment_tracker import SHIPPING_ROUTES
    return {
        "routes": [
            {
                "name": name,
                "description": route["description"],
                "chokepoints": route["chokepoints"],
                "avg_transit_days": route["avg_transit_days"]
            }
            for name, route in SHIPPING_ROUTES.items()
        ]
    }


@app.get("/locations")
async def get_locations():
    """
    Returns all 30 monitored port and chokepoint locations
    """
    from weather_monitor import MONITORED_LOCATIONS
    return {
        "total": len(MONITORED_LOCATIONS),
        "locations": MONITORED_LOCATIONS
    }