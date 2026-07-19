import os
import time
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

# Weather cache — 15 minute TTL
weather_cache = {
    "data": None,
    "timestamp": 0
}
CACHE_DURATION = 900  # 15 minutes in seconds

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
        global weather_cache

        # Return cached data if still fresh
        if weather_cache["data"] and (time.time() - weather_cache["timestamp"]) < CACHE_DURATION:
            print("Returning cached weather data")
            return weather_cache["data"]

        # Fetch fresh data
        print("Fetching fresh weather data...")
        from weather_monitor import monitor_all_ports
        all_results, risk_alerts = monitor_all_ports()

        result = {
            "summary": {
                "total_monitored": len(all_results),
                "risk_locations": len(risk_alerts),
                "all_locations": all_results
            },
            "alerts": risk_alerts
        }

        # Store in cache
        weather_cache["data"] = result
        weather_cache["timestamp"] = time.time()

        return result

    except Exception as e:
        print(f"Error in /weather endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/shipment")
async def analyze_shipment(request: ShipmentRequest):
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
    from weather_monitor import MONITORED_LOCATIONS
    return {
        "total": len(MONITORED_LOCATIONS),
        "locations": MONITORED_LOCATIONS
    }