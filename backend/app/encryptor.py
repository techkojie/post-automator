# app/encryptor.py
import os
from cryptography.fernet import Fernet
from app.logger import logger

KEY_FILE = os.path.join(os.path.dirname(__file__), "..", "secret.key")

def _load_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    try:
        os.chmod(KEY_FILE, 0o600)
    except Exception:
        pass
    return key

_key = _load_or_create_key()
fernet = Fernet(_key)

def encrypt_text(plaintext: str) -> str:
    try:
        return fernet.encrypt(plaintext.encode()).decode()
    except Exception:
        logger.exception("encrypt_text failed")
        raise

def decrypt_text(token: str) -> str:
    try:
        return fernet.decrypt(token.encode()).decode()
    except Exception:
        logger.exception("decrypt_text failed")
        raise
