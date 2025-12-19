# telegram_bot.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        raise ValueError("Telegram credentials missing in .env")

def send_telegram_message(message: str):
    """
    Sends a message to your Telegram account via bot.
    """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Raise an error for HTTP errors
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return {"error": str(e)}
    finally:
        print("✅ Telegram message function executed.")
