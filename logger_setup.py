# app/logger.py
import logging, os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "autopost.log")

logger = logging.getLogger("autopost")
logger.setLevel(logging.DEBUG)

fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(module)s:%(lineno)d | %(message)s")

fh = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=5)
fh.setFormatter(fmt); fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler(); ch.setFormatter(fmt); ch.setLevel(logging.INFO)

logger.addHandler(fh); logger.addHandler(ch)
