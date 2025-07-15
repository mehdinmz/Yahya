
# ─── Imports Library───
import os
import json
import logging
from telethon import TelegramClient, Button, events
from telethon.tl.custom.message import Message
from APIrequirements import API_ID, API_hash

# ─── Configs ───
DATA_FILE = "user_data.json"
SESSION_DIR = "session"
SESSION_FILE = os.path.join(SESSION_DIR, ".session")

# ─── Logging Setup ───
logging.basicConfig(
    format='[%(levelname)s %(asctime)s] %(name)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
os.makedirs(SESSION_DIR, exist_ok=True)
client = TelegramClient(session=SESSION_FILE, api_id=API_ID, api_hash=API_hash)

# ─── User Data Handling ───
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading data: {e}")
            return {}
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving data: {e}")

user_data = load_data()  # { user_id: { "gap_list": [], "target_list": [] } }
logger.info("User data loaded.")

# ─── /start Command Handler ───
@client.on(events.NewMessage(pattern="/start", func=lambda e: e.is_private))
async def start_handler(event: Message):
    user_id = str(event.sender_id)
    if user_id not in user_data:
        user_data[user_id] = {"gap_list": [], "target_list": []}
        save_data(user_data)
        logger.info(f"New user registered: {user_id}")

    try:
        await event.respond("Welcome to Monitoring Bot.
Use /help to show commands.")
    except Exception as e:
        logger.error(f"Failed to respond to /start: {e}")

# ─── /help Command Handler ───
@client.on(events.NewMessage(pattern="/help", func=lambda e: e.is_private))
async def help_handler(event: Message):
    try:
        await event.respond(
            "🛠 Available Commands:
"
            "/start - Start the bot
"
            "/help - Show this help message
"
        )
    except Exception as e:
        logger.error(f"Failed to respond to /help: {e}")

# ─── Main ───
def main():
    logger.info("Bot is starting...")
    client.start()
    client.run_until_disconnected()

if __name__ == "__main__":
    main()
