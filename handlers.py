import re
import csv
import io
from datetime import datetime

from telethon import TelegramClient, events
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import UserAlreadyParticipantError, InviteHashExpiredError, FloodWaitError
from telethon.tl.types import User as TelegramUser

from db import (
    create_user, get_user, add_target, get_user_targets,
    remove_target, set_target_filter, get_target_by_username, 
    clear_target_filter, get_user_messages
)
from filters import validate_filter_input, get_target_filter_summary_safe


class CommandHandlers:
    def __init__(self, client: TelegramClient):
        self.client = client
        self.register_handlers()

    def register_handlers(self):
        """Register all command handlers"""
        self.client.add_event_handler(self.handle_start, events.NewMessage(pattern=r'^/start'))
        self.client.add_event_handler(self.handle_newtarget, events.NewMessage(pattern=r'^/newtarget'))
        self.client.add_event_handler(self.handle_viewtargets, events.NewMessage(pattern=r'^/viewtargets'))
        self.client.add_event_handler(self.handle_removetarget, events.NewMessage(pattern=r'^/removetarget'))
        self.client.add_event_handler(self.handle_setfilter, events.NewMessage(pattern=r'^/setfilter'))
        self.client.add_event_handler(self.handle_viewfilter, events.NewMessage(pattern=r'^/viewfilter'))
        self.client.add_event_handler(self.handle_clearfilter, events.NewMessage(pattern=r'^/clearfilter'))
        self.client.add_event_handler(self.handle_export, events.NewMessage(pattern=r'^/export'))
        self.client.add_event_handler(self.handle_help, events.NewMessage(pattern=r'^/help'))

        print("✅ Command handlers registered")

    async def handle_start(self, event):
        """Handle /start command"""
        try:
            sender = await event.get_sender()
            user = create_user(
                telegram_id=sender.id,
                username=sender.username,
                first_name=sender.first_name
            )

            welcome_message = f"""
🚀 **Welcome to Yahya UserBot!**

Hello {sender.first_name}! Your account has been registered.

**Available Commands:**
• `/newtarget @username group_link` - Add a new target to monitor
• `/viewtargets` - View all your active targets
• `/removetarget @username` - Remove a target
• `/setfilter @username` - Set filters for a specific target
• `/viewfilter @username` - View filters for a target
• `/clearfilter @username` - Clear all filters for a target
• `/export` - Export all tracked messages as CSV
• `/help` - Show this help message

**Example:**
`/newtarget @johndoe https://t.me/+AbCdEfGhIjKlMnOp`
`/setfilter @johndoe keywords:bitcoin,crypto language:en`

Happy monitoring! 🎯
"""
            await event.reply(welcome_message)

        except Exception as e:
            print(f"❌ Error in handle_start: {e}")
            await event.reply("❌ An error occurred while processing your request.")

    async def handle_newtarget(self, event):
        """Handle /newtarget command"""
        try:
            sender = await event.get_sender()
            user = get_user(sender.id)

            if not user:
                await event.reply("❌ Please run /start first to register your account.")
                return

            # Expect command: /newtarget @username group_link
            args = event.message.text.split(' ', 2)
            if len(args) < 3:
                await event.reply(
                    "❌ Usage: `/newtarget @username group_link`\n"
                    "Example: `/newtarget @johndoe https://t.me/+AbCdEfGhIjKlMnOp`"
                )
                return

            target_username = args[1].replace('@', '')
            group_link = args[2]

            # Join group first and get entity
            group_entity = await self.join_group(group_link)
            if not group_entity:
                await event.reply("❌ Failed to join the group. Please check the link and try again.")
                return

            # Fix group_id to match real chat_id format (-100...)
            real_group_id = group_entity.id
            if not str(real_group_id).startswith("-100"):
                real_group_id = int(f"-100{real_group_id}")

            # Get target user entity
            try:
                target_entity = await self.client.get_entity(target_username)
                if not isinstance(target_entity, TelegramUser):
                    await event.reply("❌ Target must be a user, not a channel or group.")
                    return
            except Exception:
                await event.reply(f"❌ Could not find user @{target_username}. Make sure the username is correct.")
                return

            # Add target to DB with corrected group_id
            target = add_target(
                user_id=user.id,
                target_telegram_id=target_entity.id,
                target_username=target_username,
                group_id=real_group_id,
                group_name=getattr(group_entity, 'title', None),
                group_username=getattr(group_entity, 'username', None)
            )

            success_message = f"""
✅ **Target Added Successfully!**

**Target:** @{target_username}
**Group:** {group_entity.title}
**Group ID:** {real_group_id}

I will now monitor messages from @{target_username} in this group and forward them to you.

Use `/setfilter @{target_username}` to set specific filters for this target.
"""
            await event.reply(success_message)

        except Exception as e:
            print(f"❌ Error in handle_newtarget: {e}")
            await event.reply("❌ An error occurred while adding the target.")

    async def join_group(self, group_link):
        """Join a group by link or get the entity if already joined"""
        try:
            if 't.me/+' in group_link:
                invite_hash = group_link.split('t.me/+')[1]
                result = await self.client(ImportChatInviteRequest(invite_hash))
                chat = result.chats[0] if result.chats else None
                if chat:
                    print(f"✅ Joined private group: {chat.title} (ID: {chat.id})")
                return chat

            elif 't.me/' in group_link:
                username = group_link.split('t.me/')[1]
                entity = await self.client.get_entity(username)
                await self.client(JoinChannelRequest(entity))
                print(f"✅ Joined public group: {entity.title} (ID: {entity.id})")
                return entity

            else:
                entity = await self.client.get_entity(group_link)
                await self.client(JoinChannelRequest(entity))
                print(f"✅ Joined by username: {entity.title} (ID: {entity.id})")
                return entity

        except UserAlreadyParticipantError:
            entity = await self.client.get_entity(group_link)
            print(f"✅ Already in group: {entity.title} (ID: {entity.id})")
            return entity

        except Exception as e:
            print(f"❌ Error joining group: {e}")
            return None

    async def handle_viewtargets(self, event):
        """Handle /viewtargets command"""
        try:
            sender = await event.get_sender()
            user = get_user(sender.id)

            if not user:
                await event.reply("❌ Please run /start first to register your account.")
                return

            targets = get_user_targets(user.id)

            if not targets:
                await event.reply("📭 You have no active targets. Use `/newtarget @username group_link` to add one.")
                return

            message = "🎯 **Your Active Targets:**\n\n"

            for i, target in enumerate(targets, 1):
                filter_status = "No filters" if not any([target.keywords, target.language, target.media_types]) else "Filtered"
                message += f"**{i}.** @{target.target_username}\n"
                message += f"   📍 Group: {target.group_name}\n"
                message += f"   🔧 Status: {filter_status}\n"
                message += f"   📅 Added: {target.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"

            await event.reply(message)

        except Exception as e:
            print(f"❌ Error in handle_viewtargets: {e}")
            await event.reply("❌ An error occurred while retrieving your targets.")

    async def handle_removetarget(self, event):
        """Handle /removetarget command"""
        try:
            sender = await event.get_sender()
            user = get_user(sender.id)

            if not user:
                await event.reply("❌ Please run /start first to register your account.")
                return

            args = event.message.text.split(' ', 1)
            if len(args) < 2:
                await event.reply("❌ Usage: `/removetarget @username`\nExample: `/removetarget @johndoe`")
                return

            target_username = args[1].replace('@', '')

            success = remove_target(user.id, target_username)

            if success:
                await event.reply(f"✅ Target @{target_username} has been removed from monitoring.")
            else:
                await event.reply(f"❌ Target @{target_username} not found in your active targets.")

        except Exception as e:
            print(f"❌ Error in handle_removetarget: {e}")
            await event.reply("❌ An error occurred while removing the target.")

    async def handle_setfilter(self, event):
        """Handle /setfilter command"""
        try:
            sender = await event.get_sender()
            user = get_user(sender.id)

            if not user:
                await event.reply("❌ Please run /start first to register your account.")
                return

            text = event.message.text.replace('/setfilter', '').strip()

            if not text:
                help_message = """
🔧 **Set Target Filters**

Usage: `/setfilter @username keywords:word1,word2 language:en media:text,photo`

**Parameters:**
• `keywords:` - Comma-separated keywords to match
• `language:` - Language code (en, fa, ar, fr, de, es, it, ru, zh, ja, ko)
• `media:` - Media types (text, photo, video, audio, image, document, media)

**Examples:**
• `/setfilter @johndoe keywords:bitcoin,crypto language:en`
• `/setfilter @alice media:photo,video`
• `/setfilter @bob keywords:important language:fa media:text`

**To view filters:** `/viewfilter @username`
**To clear filters:** `/clearfilter @username`
"""
                await event.reply(help_message)
                return

            # Parse username and filter parameters
            parts = text.split(' ', 1)
            if len(parts) < 2:
                await event.reply("❌ Usage: `/setfilter @username [filter_parameters]`")
                return

            target_username = parts[0].replace('@', '')
            filter_text = parts[1]

            # Check if target exists
            target = get_target_by_username(user.id, target_username)
            if not target:
                await event.reply(f"❌ Target @{target_username} not found in your active targets.")
                return

            keywords, language, media_types = None, None, None

            # Parse filter parameters
            keyword_match = re.search(r'keywords?:([^,\s]+(?:,[^,\s]+)*)', filter_text, re.IGNORECASE)
            if keyword_match:
                keywords = keyword_match.group(1)

            language_match = re.search(r'language?:([a-z]{2})', filter_text, re.IGNORECASE)
            if language_match:
                language = language_match.group(1).lower()

            media_match = re.search(r'media:([^,\s]+(?:,[^,\s]+)*)', filter_text, re.IGNORECASE)
            if media_match:
                media_types = media_match.group(1)

            # Validate filter input
            errors = validate_filter_input(keywords, language, media_types)
            if errors:
                await event.reply("❌ **Filter Validation Errors:**\n" + "\n".join(errors))
                return

            # Set target filter
            updated_target = set_target_filter(user.id, target_username, keywords, language, media_types)
            if not updated_target:
                await event.reply(f"❌ Failed to set filter for @{target_username}.")
                return

            # Use the safe method to get filter summary
            filter_summary = get_target_filter_summary_safe(user.id, target_username)
            await event.reply(f"✅ **Filters Updated for @{target_username}!**\n\n{filter_summary}")

        except Exception as e:
            print(f"❌ Error in handle_setfilter: {e}")
            await event.reply("❌ An error occurred while setting the filter.")

    async def handle_viewfilter(self, event):
        """Handle /viewfilter command"""
        try:
            sender = await event.get_sender()
            user = get_user(sender.id)

            if not user:
                await event.reply("❌ Please run /start first to register your account.")
                return

            args = event.message.text.split(' ', 1)
            if len(args) < 2:
                await event.reply("❌ Usage: `/viewfilter @username`\nExample: `/viewfilter @johndoe`")
                return

            target_username = args[1].replace('@', '')

            # Check if target exists
            target = get_target_by_username(user.id, target_username)
            if not target:
                await event.reply(f"❌ Target @{target_username} not found in your active targets.")
                return

            # Use the safe method to get filter summary
            filter_summary = get_target_filter_summary_safe(user.id, target_username)
            await event.reply(f"🔧 **Current Filters for @{target_username}:**\n\n{filter_summary}")

        except Exception as e:
            print(f"❌ Error in handle_viewfilter: {e}")
            await event.reply("❌ An error occurred while retrieving the filter.")

    async def handle_clearfilter(self, event):
        """Handle /clearfilter command"""
        try:
            sender = await event.get_sender()
            user = get_user(sender.id)

            if not user:
                await event.reply("❌ Please run /start first to register your account.")
                return

            args = event.message.text.split(' ', 1)
            if len(args) < 2:
                await event.reply("❌ Usage: `/clearfilter @username`\nExample: `/clearfilter @johndoe`")
                return

            target_username = args[1].replace('@', '')

            # Check if target exists
            target = get_target_by_username(user.id, target_username)
            if not target:
                await event.reply(f"❌ Target @{target_username} not found in your active targets.")
                return

            success = clear_target_filter(user.id, target_username)

            if success:
                await event.reply(f"✅ All filters have been cleared for @{target_username}.")
            else:
                await event.reply(f"❌ Failed to clear filters for @{target_username}.")

        except Exception as e:
            print(f"❌ Error in handle_clearfilter: {e}")
            await event.reply("❌ An error occurred while clearing the filter.")

    async def handle_export(self, event):
        """Handle /export command"""
        try:
            sender = await event.get_sender()
            user = get_user(sender.id)

            if not user:
                await event.reply("❌ Please run /start first to register your account.")
                return

            messages = get_user_messages(user.id)

            if not messages:
                await event.reply("📭 No tracked messages found for export.")
                return

            csv_content = io.StringIO()
            writer = csv.writer(csv_content)
            writer.writerow([
                'Message ID',
                'Target Username',
                'Group Name',
                'Message Text',
                'Media Type',
                'Original Date',
                'Tracked Date'
            ])

            for msg in messages:
                writer.writerow([
                    msg.message_id,
                    msg.target.target_username,
                    msg.target.group_name,
                    msg.message_text or '',
                    msg.media_type or 'text',
                    msg.original_date.strftime('%Y-%m-%d %H:%M:%S') if msg.original_date else '',
                    msg.forwarded_at.strftime('%Y-%m-%d %H:%M:%S')
                ])

            csv_bytes = csv_content.getvalue().encode('utf-8')
            filename = f"yahya_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            await event.reply(
                f"📊 **Export Complete!**\n\n"
                f"**Total Messages:** {len(messages)}\n"
                f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                file=(csv_bytes, filename)
            )

        except Exception as e:
            print(f"❌ Error in handle_export: {e}")
            await event.reply("❌ An error occurred while exporting your data.")

    async def handle_help(self, event):
        """Handle /help command"""
        try:
            help_message = """
🚀 **Yahya UserBot - Command Reference**

**📋 Target Management:**
• `/newtarget @username group_link` - Add a new target to monitor
• `/viewtargets` - View all your active targets
• `/removetarget @username` - Remove a target

**🔧 Filter Management (Per Target):**
• `/setfilter @username [parameters]` - Set filters for a specific target
• `/viewfilter @username` - View filters for a target
• `/clearfilter @username` - Clear all filters for a target

**📊 Data Management:**
• `/export` - Export all tracked messages as CSV file

**ℹ️ Information:**
• `/help` - Show this help message
• `/start` - Register your account and show welcome message

**Filter Examples:**
• `/setfilter @johndoe keywords:bitcoin,crypto language:en`
• `/setfilter @alice media:photo,video`
• `/setfilter @bob keywords:important language:fa media:text`
"""
            await event.reply(help_message)
        except Exception as e:
            print(f"❌ Error in handle_help: {e}")
            await event.reply("❌ An error occurred while showing help.")