# niche_updater.py
from collections import Counter
from database import SessionLocal, Post, User
from logger_setup import logger
from textblob import TextBlob

def extract_keywords(text):
    try:
        blob = TextBlob(text)
        return [w.lower() for w, pos in blob.tags if pos.startswith("NN") or pos.startswith("JJ")]
    except Exception:
        logger.exception("extract_keywords error")
        return []

def compute_user_niche(user_id, top_n=8):
    session = SessionLocal()
    try:
        posts = session.query(Post).filter(Post.user_id == user_id).all()
        if not posts:
            logger.info("No posts for user %s", user_id)
            return []
        all_words = []
        for p in posts:
            all_words.extend(extract_keywords(p.content))
        counts = Counter(all_words)
        top = [w for w, _ in counts.most_common(top_n)]
        logger.info("Computed niche for user %s: %s", user_id, top)
        return top
    except Exception:
        logger.exception("compute_user_niche error")
        return []
    finally:
        session.close()

def apply_niche_to_user(user_id, niche_list):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("apply_niche_to_user: user not found")
            return False
        user.preferred_tone = ",".join(niche_list)
        session.add(user); session.commit()
        logger.info("Updated user %s preferred_tone to %s", user_id, user.preferred_tone)
        return True
    except Exception:
        logger.exception("apply_niche_to_user failed")
        session.rollback()
        return False
    finally:
        session.close()

def auto_update_niches_all_users():
    session = SessionLocal()
    try:
        users = session.query(User).all()
        for u in users:
            niche = compute_user_niche(u.id)
            if niche:
                apply_niche_to_user(u.id, niche)
    except Exception:
        logger.exception("auto_update_niches_all_users failed")
    finally:
        session.close()
