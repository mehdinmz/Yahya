import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# ✅ Telegram API credentials
API_ID = os.getenv("API_ID", "0")
API_HASH = os.getenv("API_HASH", "")

# ✅ Project base directory (absolute path)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Session settings
SESSION_FOLDER = os.path.join(BASE_DIR, 'session')
SESSION_NAME = 'userbot'
SESSION_PATH = os.path.join(SESSION_FOLDER, SESSION_NAME)

# ✅ Ensure session folder exists
os.makedirs(SESSION_FOLDER, exist_ok=True)

# ✅ Database settings (absolute path)
DATABASE_NAME = os.path.join(BASE_DIR, 'yahya.db')
DATABASE_URL = f"sqlite:///{DATABASE_NAME}"

# ✅ Debug mode
DEBUG = True

def validate_config():
    """Validate required configs"""
    if not API_ID or API_ID == "0":
        raise ValueError("❌ API_ID is missing or invalid. Please set it in your .env")
    if not API_HASH:
        raise ValueError("❌ API_HASH is missing. Please set it in your .env")
    
    print(f"✅ Config validated successfully")
    print(f"📁 Session path: {SESSION_PATH}")
    print(f"🗄️ Database path: {DATABASE_NAME}")