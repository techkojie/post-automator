# Post Automator – Smart Content Curator with Telegram Approval

A Python-based automation tool that scrapes news/headlines, analyzes relevance to your niche, sends drafts to Telegram for approval, and auto-posts approved content.

Built for consistent, human-controlled social media posting (great for Web3 creators).

## Features
- Web scraping from RSS/HTML sources (scraper.py)
- Content analysis & niche relevance (analyzer.py)
- Auto niche learning from past posts (niche_updater.py)
- Telegram bot with approval workflow (telegram_bot.py)
- Secure logging (logger_setup.py)
- Multi-platform ready (extendable connectors)

## Tech Stack (from requirements.txt)
- FastAPI + Uvicorn
- SQLAlchemy + Alembic + psycopg2 (PostgreSQL)
- spaCy (analysis)
- Celery + Redis (tasks)
- Tweepy (Twitter/X posting)
- cryptography (secure keys)
- Requests + aiohttp

## Quick Start
```bash
git clone https://github.com/techkojie/post-automator.git
cd post-automator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

cp .env.example .env  # Create this with your keys
alembic upgrade head
# Run your main command (e.g., uvicorn or scraper)
