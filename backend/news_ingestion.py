import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Keywords that indicate supply chain relevance
SUPPLY_CHAIN_KEYWORDS = [
    "supply chain",
    "port strike",
    "shipping delay",
    "cargo disruption",
    "suez canal",
    "strait of malacca",
    "freight disruption",
    "logistics disruption",
    "shipping route",
    "container shortage",
    "port congestion",
    "trade disruption",
    "red sea",
    "taiwan strait"
]

def fetch_supply_chain_news(days_back=1):
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    query = "port strike OR shipping delay OR supply chain disruption OR cargo OR freight OR semiconductor shortage OR trade war OR suez canal OR red sea shipping"
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 20,
        "apiKey": NEWS_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = []
        for article in data.get("articles", []):
            if not article.get("title") or not article.get("description"):
                continue
            clean_article = {
                "title": article["title"],
                "description": article["description"],
                "content": article.get("content", article["description"]),
                "url": article["url"],
                "source": article["source"]["name"],
                "published_at": article["publishedAt"]
            }
            articles.append(clean_article)
        print(f"Fetched {len(articles)} articles successfully")

        print("Sample titles fetched:")
        for a in articles[:5]:
           print(f"  - {a['title']}")
        return articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []


def is_supply_chain_relevant(article):
    text = (article["title"] + " " + article["description"]).lower()
    for keyword in SUPPLY_CHAIN_KEYWORDS:
        if keyword.lower() in text:
            return True
    return False


def get_filtered_articles():
    articles = fetch_supply_chain_news(days_back=7)
    filtered = [a for a in articles if is_supply_chain_relevant(a)]
    
    if len(filtered) < 3:
        print(f"Only {len(filtered)} filtered — adding unfiltered articles")
        extra = [a for a in articles if a not in filtered]
        filtered = filtered + extra[:5]
    
    print(f"Filtered to {len(filtered)} supply chain relevant articles")
    return filtered


if __name__ == "__main__":
    articles = get_filtered_articles()
    for i, article in enumerate(articles[:3]):
        print(f"\n--- Article {i+1} ---")
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Published: {article['published_at']}")
        print(f"Description: {article['description'][:100]}...")