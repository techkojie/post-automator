# scraper.py
import time
import random
import feedparser
import requests
from bs4 import BeautifulSoup
from logger_setup import logger
from database import SessionLocal, Draft

SOURCES = [
    {"type": "rss", "url": "https://news.google.com/rss"},
    {"type": "rss", "url": "https://feeds.abcnews.com/abcnews/topstories"},
    {"type": "rss", "url": "https://moxie.foxnews.com/feed.xml"},
    {"type": "html", "url": "https://www.reuters.com"},
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
]

def _is_duplicate(session, title, source):
    return session.query(Draft).filter(Draft.content == title, Draft.source == source).first() is not None

def _fetch_url(url, retries=3):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                return r.text
            elif r.status_code == 429:
                logger.warning("429 from %s — backing off", url)
                time.sleep(60)
        except Exception as e:
            logger.warning("Fetch error %s: %s", url, e)
        time.sleep(random.uniform(2, 5))
    return None

def scrape_ideas(limit_per_source=5):
    session = SessionLocal()
    new_drafts = []
    try:
        for src in SOURCES:
            logger.info("Scraping %s", src["url"])
            if src["type"] == "rss":
                try:
                    feed = feedparser.parse(src["url"])
                    entries = feed.entries[:limit_per_source]
                    for entry in entries:
                        title = getattr(entry, "title", "").strip()
                        summary = getattr(entry, "summary", title)
                        if not title:
                            continue
                        if _is_duplicate(session, title, src["url"]):
                            continue
                        d = Draft(content=title, source=src["url"], status="pending")
                        session.add(d); new_drafts.append(d)
                except Exception as e:
                    logger.exception("RSS parse error for %s", src["url"])
            else:
                html = _fetch_url(src["url"])
                if not html:
                    continue
                soup = BeautifulSoup(html, "html.parser")
                headlines = soup.find_all(["h1","h2","h3"], limit=limit_per_source)
                for h in headlines:
                    title = h.get_text(strip=True)
                    if not title:
                        continue
                    if _is_duplicate(session, title, src["url"]):
                        continue
                    d = Draft(content=title, source=src["url"], status="pending")
                    session.add(d); new_drafts.append(d)
            time.sleep(random.uniform(2,6))
        session.commit()
        logger.info("Scraper saved %d new drafts", len(new_drafts))
    except Exception as e:
        logger.exception("scrape_ideas failed")
        session.rollback()
    finally:
        session.close()
    return new_drafts

def is_duplicate(session, title, source):
    return (
        session.query(Post)
        .filter(Post.title == title, Post.source == source)
        .first()
        is not None
    )

# Helper: safe request with retries and rate-limiting
def fetch_url(url, max_retries=5):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:
                print(f"⚠️ Rate limit hit for {url}. Waiting before retry...")
                time.sleep(60)
            else:
                print(f"⚠️ Unexpected status {response.status_code} for {url}")
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
        time.sleep(random.uniform(2, 5))
    return None

def scrape_ideas():
    """Main scraper that collects trending topics from multiple sources."""
    session = SessionLocal()
    new_posts = []  # Early return to avoid execution during comparison

    for src in SOURCES:
        print(f"🔍 Fetching from {src['url']}...")
        if src["type"] == "rss":
            try:
                feed = feedparser.parse(src["url"])
                for entry in feed.entries[:10]:  # Limit per source
                    title = entry.title.strip()
                    if not title or is_duplicate(session, title, src["url"]):
                        continue

                    post = Post(
                        title=title,
                        content=entry.get("summary", title),
                        source=src["url"],
                        sentiment="pending",
                        created_at=datetime.utcnow(),
                    )
                    session.add(post)
                    new_posts.append(post)
            except Exception as e:
                print(f"❌ RSS error from {src['url']}: {e}")

        elif src["type"] == "html":
            html = fetch_url(src["url"])
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")

            for h in soup.find_all(["h2", "h3"], limit=10):
                title = h.get_text(strip=True)
                if not title or is_duplicate(session, title, src["url"]):
                    continue
                post = Post(
                    title=title,
                    content=title,
                    source=src["url"],
                    sentiment="pending",
                    created_at=datetime.utcnow(),
                )
                session.add(post)
                new_posts.append(post)

        # Polite pause between each source
        time.sleep(random.uniform(3, 7))

    session.commit()
    session.close()

    print(f"✅ Scraped and saved {len(new_posts)} new posts.")
    return new_posts
