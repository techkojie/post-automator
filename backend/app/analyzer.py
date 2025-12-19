# analyzer.py
import os
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()

# Load niches from environment
NICHES = {
    "wordpress": os.getenv("WORDPRESS_NICHE", "").lower().split(","),
    "twitter": os.getenv("TWITTER_NICHE", "").lower().split(","),
    "truthsocial": os.getenv("TRUTHSOCIAL_NICHE", "").lower().split(","),
}

def relevance_score(text: str, niche_keywords: list) -> float:
    """Score how relevant a text is to the niche keywords."""
    text = text.lower()
    if not niche_keywords:
        return 0
    hits = sum(1 for word in niche_keywords if word.strip() in text)
    return hits / len(niche_keywords)

def analyze_content(text_list, platform="wordpress"):
    """Analyze tone and relevance for a platform."""
    results = []
    niche = NICHES.get(platform, [])
    for text in text_list:
        # Tone / sentiment
        sentiment = TextBlob(text).sentiment.polarity
        tone = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"

        # Niche matching
        relevance = relevance_score(text, niche)
        if relevance > 0.2:  # Only keep posts somewhat relevant
            results.append({
                "text": text,
                "sentiment": tone,
                "relevance": round(relevance, 2),
            })
    return results
