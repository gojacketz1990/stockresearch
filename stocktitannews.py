import feedparser
import ssl
from datetime import datetime
import textwrap
import os
import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

# ====================== CONFIG ======================
RSS_URL = "https://www.stocktitan.net/rss"
MODEL = "grok-3"
MAX_ARTICLE_LENGTH = 12000  # characters - Grok has large context but we truncate for cost/speed

# Load .env
load_dotenv(override=True)
xai_api_key = os.getenv("XAI_API_KEY")

print(f"🔑 XAI_API_KEY loaded: {'✅ YES' if xai_api_key and xai_api_key.startswith('xai-') else '❌ NO'}")

# Initialize Grok client
client = None
if xai_api_key and xai_api_key.startswith("xai-"):
    client = OpenAI(api_key=xai_api_key, base_url="https://api.x.ai/v1")
    print("✅ Grok client ready\n")
else:
    print("❌ Missing or invalid XAI_API_KEY\n")

# ====================== FETCH FULL ARTICLE ======================
def fetch_full_article(url: str) -> str:
    """Fetch and extract main article text from StockTitan page."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        # Try common content containers on StockTitan
        article_body = None
        for selector in [
            'div.article-body', 'div.news-content', 'div.post-content',
            'article', 'div#content', '.entry-content'
        ]:
            article_body = soup.select_one(selector)
            if article_body:
                break

        if not article_body:
            # Fallback: get all paragraphs
            paragraphs = soup.find_all('p')
            text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)
        else:
            text = article_body.get_text(separator='\n', strip=True)

        # Clean up
        clean_text = ' '.join(text.split())[:MAX_ARTICLE_LENGTH]
        return clean_text if len(clean_text) > 100 else "Article content too short or blocked."

    except Exception as e:
        return f"❌ Failed to fetch article: {type(e).__name__} - {str(e)}"


# ====================== GROK ANALYSIS ======================
def analyze_with_grok(title: str, article_text: str, ticker: str) -> str:
    if not client:
        return "❌ Grok client not initialized."
    if len(article_text.strip()) < 100:
        return "⚠️ Article text too short to analyze."

    prompt = f"""You are an expert financial analyst. Read the full article below and analyze its impact on ticker {ticker}.

Title: {title}
Full Article:
{article_text}

Return **only** valid JSON with these exact keys:
{{
  "sentiment": "positive"|"negative"|"neutral",
  "impact_level": "high"|"medium"|"low",
  "impact_explanation": "1-2 sentence explanation focused on stock price effect",
  "reasoning": "Key facts from the article that drive your conclusion"
}}

Only output the JSON."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=600,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content.strip()
        parsed = json.loads(content)
        return json.dumps(parsed, indent=2)
    except Exception as e:
        return f"❌ Grok API error: {str(e)}"


# ====================== MAIN FUNCTION ======================
def fetch_stock_titan_rss(limit=12):
    print("Fetching latest news from Stock Titan RSS...\n")
    
    feed = feedparser.parse(RSS_URL)
    if feed.bozo:
        print(f"❌ Feed error: {feed.bozo_exception}")
        return

    print(f"✅ Fetched {len(feed.entries)} items\n")
    print("=" * 130)

    for i, entry in enumerate(feed.entries[:limit], 1):
        title = entry.get('title', 'No Title')
        link = entry.get('link', '#')
        pub_date = entry.get('published', entry.get('pubDate'))

        ticker = "N/A"
        if "|" in title:
            ticker = title.split("|")[-1].strip().replace("Stock News", "").strip()

        time_str = "Unknown"
        if pub_date:
            try:
                dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = pub_date[:22]

        print(f"{i:2d}. [{ticker}] {time_str}")
        print(f"    {title}")
        print(f"    🔗 {link}")

        # Fetch full article
        print("    📥 Fetching full article...")
        full_text = fetch_full_article(link)

        # Grok Analysis
        print("    📊 GROK ANALYSIS (full article):")
        grok_result = analyze_with_grok(title, full_text, ticker)
        print(textwrap.indent(grok_result, "    "))
        print("-" * 130)


if __name__ == "__main__":
    fetch_stock_titan_rss(limit=10)