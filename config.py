# config.py
# Initial configuration for the bot: API, file paths, and validation

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API credentials
API_ID = os.getenv("API_ID", "0")
API_HASH = os.getenv("API_HASH", "")

# File and directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_FOLDER = os.path.join(BASE_DIR, 'session')
SESSION_NAME = 'userbot'
SESSION_PATH = os.path.join(SESSION_FOLDER, SESSION_NAME)
DATABASE_NAME = os.path.join(BASE_DIR, 'yahya.db')
DATABASE_URL = f"sqlite:///{DATABASE_NAME}"

# Create session folder if it doesn't exist
os.makedirs(SESSION_FOLDER, exist_ok=True)

# Validate required configuration values
def validate_config():
    if not API_ID or API_ID == "0":
        raise ValueError("API_ID is missing or invalid. Set it in .env")
    if not API_HASH:
        raise ValueError("API_HASH is missing. Set it in .env")