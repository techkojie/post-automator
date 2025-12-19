# social_connector.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class SocialConnector:
    def __init__(self):
        """Initialize available platform credentials."""
        self.twitter_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.linkedin_token = os.getenv("LINKEDIN_ACCESS_TOKEN")

    def post_to_twitter(self, text: str):
        """Post content to Twitter/X using the official API."""
        if not self.twitter_token:
            print("⚠️ Twitter credentials missing. Skipping post.")
            return False

        try:
            url = "https://api.x.com/2/tweets"  # Example endpoint
            headers = {"Authorization": f"Bearer {self.twitter_token}"}
            payload = {"text": text}
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 201:
                print("✅ Posted successfully to Twitter.")
                return True
            else:
                print(f"❌ Twitter error {response.status_code}: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Twitter post failed: {e}")
            return False

    def post_to_linkedin(self, text: str):
        """Post content to LinkedIn using the LinkedIn API."""
        if not self.linkedin_token:
            print("⚠️ LinkedIn credentials missing. Skipping post.")
            return False

        try:
            url = "https://api.linkedin.com/v2/ugcPosts"
            headers = {
                "Authorization": f"Bearer {self.linkedin_token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }
            payload = {
                "author": "urn:li:person:yourLinkedInID",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": text},
                        "shareMediaCategory": "NONE",
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code in (201, 200):
                print("✅ Posted successfully to LinkedIn.")
                return True
            else:
                print(f"❌ LinkedIn error {response.status_code}: {response.text}")
                return False

        except Exception as e:
            print(f"❌ LinkedIn post failed: {e}")
            return False
