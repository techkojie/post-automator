# telegram_bot.py
import os
import requests
from logger_setup import logger
from database import SessionLocal, Draft, User, Post
from social_connectors import TwitterConnector, WordPressConnector, TruthSocialConnector

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID= os.getenv("CHAT_ID")
if not TELEGRAM_TOKEN:
    logger = logger  # ensure logger import
    logger.warning("TELEGRAM_BOT_TOKEN missing in .env")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_message(chat_id, text, buttons=None):
    try:
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if buttons:
            payload["reply_markup"] = {"inline_keyboard": buttons}
        r = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        logger.exception("send_message failed")
        return None

def send_draft_for_approval(chat_id, draft_id, content):
    buttons = [
        [
            {"text": "✅ Approve & Post", "callback_data": f"approve_{draft_id}"},
            {"text": "✏️ Edit", "callback_data": f"edit_{draft_id}"},
            {"text": "❌ Reject", "callback_data": f"reject_{draft_id}"}
        ]
    ]
    return send_message(chat_id, f"📝 *Draft #{draft_id}*\n\n{content}", buttons)

def handle_callback_query(callback_data, from_chat_id):
    """
    Called by webhook when a callback dialog (inline button) is pressed.
    """
    try:
        action, draft_id = callback_data.split("_", 1)
    except Exception:
        return {"ok": False, "msg": "invalid callback format"}

    session = SessionLocal()
    try:
        draft = session.query(Draft).filter(Draft.id == int(draft_id)).first()
        if not draft:
            send_message(from_chat_id, "⚠️ Draft not found.")
            return {"ok": False, "msg": "draft not found"}

        if action == "approve":
            # Post draft to all user's connections
            user = draft.user
            posted_platforms = []
            # instantiate connectors (with real credentials you'd pass user's tokens)
            twitter = TwitterConnector()
            wp = WordPressConnector()
            ts = TruthSocialConnector()
            # do actual posts (stubs here)
            res_t = twitter.post(draft.content)
            res_wp = wp.post(title=draft.content[:60], content=draft.content, status="publish")
            res_ts = ts.post(draft.content)
            # collect results
            if res_t.get("success"): posted_platforms.append("Twitter")
            if res_wp.get("success"): posted_platforms.append("WordPress")
            if res_ts.get("success"): posted_platforms.append("TruthSocial")
            # mark as posted
            draft.status = "approved"
            p = Post(user_id=draft.user_id, platform=",".join(posted_platforms) or "none", content=draft.content, sentiment="unknown")
            session.add(p)
            session.commit()
            send_message(from_chat_id, f"✅ Draft posted to: {', '.join(posted_platforms) if posted_platforms else 'None (failed)'}")
            return {"ok": True}
        elif action == "edit":
            draft.status = "editing"
            session.add(draft); session.commit()
            send_message(from_chat_id, f"✏️ Send the new text for Draft {draft.id}. After sending, press Approve to publish.")
            return {"ok": True}
        elif action == "reject":
            draft.status = "rejected"
            session.add(draft); session.commit()
            send_message(from_chat_id, f"❌ Draft {draft.id} rejected.")
            return {"ok": True}
        else:
            send_message(from_chat_id, "⚠️ Unknown action.")
            return {"ok": False}
    except Exception:
        logger.exception("handle_callback_query error")
        session.rollback()
        return {"ok": False}
    finally:
        session.close()
