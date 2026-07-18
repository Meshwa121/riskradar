import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from knowledge_base import search_similar_disruptions

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=GEMINI_API_KEY,
    temperature=0.1
)

# Define the state that flows through all nodes
class RiskState(TypedDict):
    article_title: str
    article_description: str
    article_source: str
    article_url: str
    is_relevant: bool
    affected_routes: List[str]
    affected_industries: List[str]
    severity: str
    historical_context: str
    alert_summary: str
    recommendation: str

# ─────────────────────────────────────────────
# NODE 1 — Combined Analyzer (Nodes 1-4)
# Single API call replacing 4 separate calls
# ─────────────────────────────────────────────
def combined_analyzer(state: RiskState) -> RiskState:
    """
    Combines relevance detection, route matching,
    impact analysis and risk classification into
    one single API call — saves 3 API calls per article
    """
    print("Node 1: Running combined analysis...")

    prompt = f"""
    Analyze this news article for supply chain relevance and risk assessment.

    Title: {state['article_title']}
    Description: {state['article_description']}

    Return a JSON object with exactly these fields:
    {{
        "is_relevant": true or false,
        "affected_routes": ["route1", "route2"],
        "affected_industries": ["industry1", "industry2"],
        "severity": "Critical" or "High" or "Medium" or "Low"
    }}
      Guidelines:
    - is_relevant: true if article relates to active or emerging risks in supply chains, shipping, ports, logistics, trade routes, or industries that depend on global trade. Include semiconductor shortages, labor disputes affecting logistics, geopolitical tensions near trade routes, and commodity supply disruptions. Exclude pure opinion pieces, stock market news, and unrelated general economic forecasts.
    - affected_routes: choose from — Suez Canal, Red Sea, Strait of Malacca, Panama Canal, Taiwan Strait, Black Sea, Port of Rotterdam, Port of Los Angeles, Port of Shanghai, Indian Ocean, North Sea, Global Trade Routes
    - affected_industries: choose from — Electronics, Automotive, Oil and Gas, Consumer Goods, Food and Agriculture, Pharmaceuticals, Chemicals, Steel and Metals, Retail, Semiconductors, Textile and Apparel, Industrial Equipment
    - severity: Critical=major route blocked, High=significant disruption, Medium=manageable, Low=minor impact
    - If not relevant set affected_routes=[], affected_industries=[], severity="Low"

    Return ONLY the JSON object. No explanation, no markdown, no backticks.
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        data = json.loads(content)

        return {
            **state,
            "is_relevant": data.get("is_relevant", False),
            "affected_routes": data.get("affected_routes", []),
            "affected_industries": data.get("affected_industries", []),
            "severity": data.get("severity", "Low")
        }

    except Exception as e:
        print(f"Error in combined_analyzer: {e}")
        return {
            **state,
            "is_relevant": False,
            "affected_routes": [],
            "affected_industries": [],
            "severity": "Low"
        }

# ─────────────────────────────────────────────
# NODE 2 — Alert Generator
# Retrieves historical context + generates alert
# ─────────────────────────────────────────────
def alert_generator(state: RiskState) -> RiskState:
    """
    Retrieves similar historical disruptions from ChromaDB
    and generates final human readable alert
    """
    print("Node 2: Retrieving historical context and generating alert...")

    # Retrieve historical context from ChromaDB
    search_query = f"{state['article_title']} {state['article_description']}"
    similar = search_similar_disruptions(search_query, k=2)

    historical_context = ""
    for doc in similar:
        historical_context += f"\n{doc.page_content[:300]}...\n"

    # Generate alert with historical context
    prompt = f"""
    Generate a professional supply chain risk alert.

    News: {state['article_title']}
    Description: {state['article_description']}
    Severity: {state['severity']}
    Affected Routes: {', '.join(state['affected_routes'])}
    Affected Industries: {', '.join(state['affected_industries'])}
    Historical Context: {historical_context}

    Provide:
    SUMMARY: A 2-3 sentence alert explaining the risk and its potential impact
    RECOMMENDATION: A specific actionable recommendation for supply chain managers

    Format exactly like this:
    SUMMARY: [your summary]
    RECOMMENDATION: [your recommendation]
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content.strip()

    summary = ""
    recommendation = ""

    for line in content.split("\n"):
        if line.startswith("SUMMARY:"):
            summary = line.replace("SUMMARY:", "").strip()
        elif line.startswith("RECOMMENDATION:"):
            recommendation = line.replace("RECOMMENDATION:", "").strip()

    return {
        **state,
        "historical_context": historical_context,
        "alert_summary": summary,
        "recommendation": recommendation
    }

# ─────────────────────────────────────────────
# Routing — skip irrelevant articles
# ─────────────────────────────────────────────
def should_continue(state: RiskState) -> str:
    if state["is_relevant"]:
        return "alert_generator"
    else:
        return END

# ─────────────────────────────────────────────
# Build the optimized 2-node pipeline
# ─────────────────────────────────────────────
def build_risk_pipeline():
    workflow = StateGraph(RiskState)

    # Add 2 nodes
    workflow.add_node("combined_analyzer", combined_analyzer)
    workflow.add_node("alert_generator", alert_generator)

    # Entry point
    workflow.set_entry_point("combined_analyzer")

    # Route after node 1
    workflow.add_conditional_edges(
        "combined_analyzer",
        should_continue,
        {
            "alert_generator": "alert_generator",
            END: END
        }
    )

    # Connect node 2 to end
    workflow.add_edge("alert_generator", END)

    return workflow.compile()


def analyze_article(article: dict) -> Optional[dict]:
    """
    Main function — runs article through optimized 2-node pipeline
    """
    pipeline = build_risk_pipeline()

    initial_state = RiskState(
        article_title=article["title"],
        article_description=article["description"],
        article_source=article.get("source", ""),
        article_url=article.get("url", ""),
        is_relevant=False,
        affected_routes=[],
        affected_industries=[],
        severity="",
        historical_context="",
        alert_summary="",
        recommendation=""
    )

    result = pipeline.invoke(initial_state)

    if not result["is_relevant"]:
        print(f"Not relevant: {article['title'][:50]}")
        return None

    return {
        "title": result["article_title"],
        "source": result["article_source"],
        "url": result["article_url"],
        "published_at": article.get("published_at", "Unknown"),
        "severity": result["severity"],
        "affected_routes": result["affected_routes"],
        "affected_industries": result["affected_industries"],
        "alert_summary": result["alert_summary"],
        "recommendation": result["recommendation"],
        "historical_context": result["historical_context"]
    }


if __name__ == "__main__":
    from news_ingestion import get_filtered_articles

    print("Fetching live news articles...\n")
    articles = get_filtered_articles()

    if not articles:
        print("No articles fetched — using test article")
        articles = [{
            "title": "Port Strike at Rotterdam Disrupts European Shipping",
            "description": "Dock workers at the Port of Rotterdam have announced a 48-hour strike starting tomorrow, threatening to disrupt shipping across Northern Europe. The port handles 14.8 million containers annually.",
            "source": "Reuters",
            "url": "https://reuters.com/test"
        }]

    print(f"Processing {min(2, len(articles))} articles...\n")

    alerts = []
    for article in articles[:2]:
        print(f"\nAnalyzing: {article['title'][:60]}...")
        result = analyze_article(article)
        if result:
            alerts.append(result)
        else:
            print(f"Skipped — not relevant or no alert generated")

    print(f"\n{'='*50}")
    print(f"GENERATED {len(alerts)} RISK ALERTS")
    print(f"{'='*50}")

    for i, alert in enumerate(alerts):
        print(f"\n--- Alert {i+1} ---")
        print(f"Title: {alert['title']}")
        print(f"Source: {alert['source']}")
        print(f"Severity: {alert['severity']}")
        print(f"Routes: {', '.join(alert['affected_routes'])}")
        print(f"Industries: {', '.join(alert['affected_industries'][:3])}...")
        print(f"Summary: {alert['alert_summary']}")
        print(f"Recommendation: {alert['recommendation']}")