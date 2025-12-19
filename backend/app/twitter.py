# app/social/twitter.py
import tweepy
from app.config import TWITTER_API_KEY, TWITTER_API_SECRET
from app.encryptor import decrypt_text
from app.logger import logger

class TwitterClient:
    def __init__(self, token_encrypted: str = None, secret_encrypted: str = None):
        try:
            if not all([TWITTER_API_KEY, TWITTER_API_SECRET]):
                raise RuntimeError("TWITTER_API_KEY/SECRET not configured")
            self.api_key = TWITTER_API_KEY
            self.api_secret = TWITTER_API_SECRET
            self.access_token = decrypt_text(token_encrypted) if token_encrypted else None
            self.access_secret = decrypt_text(secret_encrypted) if secret_encrypted else None
            if self.access_token and self.access_secret:
                auth = tweepy.OAuth1UserHandler(self.api_key, self.api_secret, self.access_token, self.access_secret)
                self.client = tweepy.API(auth, wait_on_rate_limit=True)
            else:
                self.client = None
        except Exception:
            logger.exception("TwitterClient init failed")
            raise

    def post(self, text: str):
        try:
            if not self.client:
                raise RuntimeError("Twitter client not authenticated for user")
            status = self.client.update_status(status=text)
            logger.info("Tweet posted id=%s", getattr(status, "id_str", None))
            return {"success": True, "id": getattr(status, "id_str", None)}
        except Exception:
            logger.exception("Twitter post failed")
            return {"success": False}
