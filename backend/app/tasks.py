# app/tasks.py
from celery import Celery
from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from app.logger import logger
from app.database import SessionLocal
from app.models import Draft, Connection, Post
from app.social.twitter import TwitterClient

celery = Celery("autopost", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery.task(bind=True, name="post_to_twitter")
def post_to_twitter(self, draft_id: int, connection_id: int):
    session = SessionLocal()
    try:
        draft = session.get(Draft, draft_id)
        conn = session.get(Connection, connection_id)
        if not draft or not conn:
            logger.error("Invalid draft or connection")
            return {"success": False, "reason": "invalid"}
        client = TwitterClient(token_encrypted=conn.token_encrypted, secret_encrypted=conn.secret_encrypted)
        res = client.post(draft.content)
        if res.get("success"):
            p = Post(user_id=draft.user_id, platform="twitter", content=draft.content)
            session.add(p)
            draft.status = "approved"
            session.add(draft)
            session.commit()
            logger.info("Posted draft %s to twitter", draft_id)
            return {"success": True, "post_id": res.get("id")}
        else:
            logger.error("Twitter post failed for draft %s", draft_id)
            return {"success": False}
    except Exception:
        logger.exception("post_to_twitter failed")
        session.rollback()
        return {"success": False}
    finally:
        session.close()
