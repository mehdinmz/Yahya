import asyncio
import signal
import socks
import sys
from datetime import datetime

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from config import API_ID, API_HASH, SESSION_PATH, DEBUG, validate_config
from db import init_db, get_all_active_targets, save_tracked_message
from handlers import CommandHandlers
from filters import should_forward, get_media_type


class YahyaBot:
    def __init__(self):
        self.client = None
        self.handlers = None
        self.running = False

    async def initialize(self):
        """Initialize the bot"""
        try:
            print("🚀 Initializing Yahya UserBot...")

            validate_config()
            init_db()
            proxy = (socks.HTTP, '127.0.0.1', 10808)

            self.client = TelegramClient(SESSION_PATH, API_ID, API_HASH, proxy=proxy)

            self.handlers = CommandHandlers(self.client)

            self.client.add_event_handler(self.handle_new_message, events.NewMessage())

            print("✅ Bot initialized successfully")

        except Exception as e:
            print(f"❌ Failed to initialize bot: {e}")
            raise

    async def start(self):
        """Start the bot"""
        try:
            print("🔐 Starting Telegram client...")

            await self.client.start()

            if not await self.client.is_user_authorized():
                print("❌ User not authorized. Please check your session.")
                return False

            me = await self.client.get_me()
            print(f"✅ Logged in as: {me.first_name} (@{me.username})")

            self.running = True
            print("🎯 Yahya UserBot is now running and monitoring targets...")

            try:
                await self.client.run_until_disconnected()
            except KeyboardInterrupt:
                print("\n⏹️ Bot stopped by user")
            finally:
                self.running = False

        except SessionPasswordNeededError:
            print("❌ Two-factor authentication enabled. Please enter your password.")
            password = input("Password: ")
            await self.client.sign_in(password=password)
            await self.start()

        except Exception as e:
            print(f"❌ Error starting bot: {e}")
            return False

        return True

    async def handle_new_message(self, event):
        """Handle new messages and check if they should be forwarded"""
        try:
            if not event.is_group and not event.is_channel:
                return

            real_sender_id = getattr(event.message.from_id, "user_id", None)

            if event.message.forward:
                if hasattr(event.message.forward, 'from_id'):
                    real_sender_id = getattr(event.message.forward.from_id, "user_id", None)
                elif hasattr(event.message.forward, 'original_sender_id'):
                    real_sender_id = event.message.forward.original_sender_id

            if real_sender_id is None:
                if DEBUG:
                    print("[DEBUG] No sender ID → skip")
                return

            if DEBUG:
                print(f"[DEBUG] Incoming msg → sender_id: {real_sender_id}, chat_id: {event.chat_id}")

            targets = get_all_active_targets()
            if not targets:
                return

            matched_targets = [
                target
                for target in targets
                if target.target_telegram_id == real_sender_id
                and target.group_id == event.chat_id
            ]

            if DEBUG:
                print(f"[DEBUG] Found {len(matched_targets)} matched targets")

            if not matched_targets:
                if DEBUG:
                    print("[DEBUG] No matched targets for this sender/group")
                return

            for target in matched_targets:
                if should_forward(event.message, target.user_id):
                    await self.forward_message(event, target)
                    if DEBUG:
                        print(f"[DEBUG] ✅ Forwarded → @{target.target_username}")
                else:
                    if DEBUG:
                        print(f"[DEBUG] ❌ Filtered → @{target.target_username}")

        except Exception as e:
            print(f"❌ Error in handle_new_message: {e}")

    async def forward_message(self, event, target):
        """Forward message to user and save to database"""
        try:
            message_text = event.message.text or event.message.message or ""
            media_type = get_media_type(event.message)
            original_date = event.message.date

            reply_info = ""
            reply_msg = None

            if event.message.is_reply:
                reply_msg = await event.message.get_reply_message()
                if reply_msg:
                    reply_sender_id = getattr(reply_msg.from_id, "user_id", None)
                    reply_sender = f"User ID: {reply_sender_id}" if reply_sender_id else "Unknown"
                    reply_info = f"\n📌 This message is a reply to: {reply_sender}"

            forward_header = f"""
🎯 **New Message from Target**

**From:** @{target.target_username}
**Group:** {target.group_name}
**Time:** {original_date.strftime('%Y-%m-%d %H:%M:%S')}
**Type:** {media_type}
{reply_info}
{'─' * 30}
            """

            user_entity = await self.client.get_entity(target.user.telegram_id)

            # توضیح
            await self.client.send_message(user_entity, forward_header.strip())

            if reply_msg:
                forwarded_original = await self.client.forward_messages(
                    user_entity,
                    reply_msg,
                    silent=True
                )

                await self.client.send_message(
                    user_entity,
                    message_text,
                    reply_to=forwarded_original.id
                )

            else:
                await self.client.forward_messages(
                    user_entity,
                    event.message,
                    silent=True
                )

            save_tracked_message(
                target_id=target.id,
                message_id=event.message.id,
                message_text=message_text,
                media_type=media_type,
                original_date=original_date
            )

            if DEBUG:
                print(f"✅ Saved to DB → @{target.target_username}")

        except Exception as e:
            print(f"❌ Error forwarding message: {e}")


bot = YahyaBot()


async def main():
    """Main function to run the bot"""
    try:
        await bot.initialize()
        await bot.start()

    except Keyboard:
        print("\n⏹️ Received interrupt signal")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        await bot.stop()


def signal_handler(signum, frame):
    """Handle system signals"""
    print(f"\n📡 Received signal {signum}")
    asyncio.create_task(bot.stop())
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    ██    ██  █████  ██   ██ ██    ██  █████                  ║
    ║     ██  ██  ██   ██ ██   ██  ██  ██  ██   ██                 ║
    ║      ████   ███████ ███████   ████   ███████                 ║
    ║       ██    ██   ██ ██   ██    ██    ██   ██                 ║
    ║       ██    ██   ██ ██   ██    ██    ██   ██                 ║
    ║                                                              ║
    ║           🎯 Telegram UserBot for Target Monitoring         ║
    ║                                                              ║
    ║                    Production-Grade v2.0                     ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """

    print(banner)
    print("🚀 Starting Yahya UserBot...")
    print("📅 Startup time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("─" * 60)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)
