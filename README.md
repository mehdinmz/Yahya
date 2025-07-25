# 🎯 Yahya UserBot - Advanced Telegram Target Monitoring

A production-grade Python Telegram UserBot built with **Telethon** for real-time message monitoring, filtering, and forwarding. Monitor specific users across multiple groups with advanced filtering capabilities.

## 🚀 Features

- **🎯 Target Monitoring**: Monitor specific users across multiple Telegram groups
- **⚡ Real-time Forwarding**: Instantly forward matching messages to your private chat
- **🔍 Advanced Filters**: Filter by keywords, language, and media types
- **💾 SQLite Database**: Store all tracked messages with full details
- **📊 Data Export**: Export all tracked messages as CSV files
- **🛡️ Robust Error Handling**: Graceful handling of all edge cases
- **🔐 Session Management**: Secure session storage and management

## 📋 Requirements

- Python 3.8+
- Telegram API credentials (API_ID and API_HASH)
- Your personal Telegram account

## 🛠️ Installation

1. **Clone or download the project files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Telegram API credentials:**
   - Go to https://my.telegram.org/apps
   - Create a new application
   - Note down your `API_ID` and `API_HASH`

4. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your API credentials:
   ```bash
   API_ID=your_api_id_here
   API_HASH=your_api_hash_here
   ```

## 🎮 Usage

### Start the Bot

```bash
python bot.py
```

On first run, you'll be prompted to:
1. Enter your phone number
2. Enter the verification code sent to your Telegram
3. Enter your 2FA password (if enabled)

### Available Commands

#### 📋 Target Management
- `/start` - Register your account and show welcome message
- `/newtarget @username group_link` - Add a new target to monitor
- `/viewtargets` - View all your active targets
- `/removetarget @username` - Remove a target from monitoring

#### 🔧 Filter Management
- `/setfilter` - Set message filters (keywords, language, media types)
- `/viewfilter` - View current active filters

#### 📊 Data Management
- `/export` - Export all tracked messages as CSV file
- `/help` - Show command reference

### Command Examples

**Add a new target:**
```
/newtarget @johndoe https://t.me/+AbCdEfGhIjKlMnOp
```

**Set filters:**
```
/setfilter keywords:bitcoin,crypto language:en media:text,photo
```

**Remove a target:**
```
/removetarget @johndoe
```

## 🔧 Advanced Filtering

### Keywords Filter
Monitor messages containing specific keywords:
```
/setfilter keywords:bitcoin,ethereum,trading
```

### Language Filter
Filter messages by language (using automatic detection):
```
/setfilter language:en
```
Supported languages: `en`, `fa`, `ar`, `fr`, `de`, `es`, `it`, `ru`, `zh`, `ja`, `ko`

### Media Type Filter
Filter by message content type:
```
/setfilter media:text,photo,video
```
Supported types: `text`, `photo`, `video`, `audio`, `image`, `document`, `media`

### Combined Filters
Use multiple filters together:
```
/setfilter keywords:important,urgent language:en media:text
```

### Clear All Filters
```
/setfilter clear
```

## 🗃️ Database Schema

The bot uses SQLite with the following tables:

- **Users**: Store user information
- **Targets**: Store target monitoring configuration
- **Filters**: Store user-specific filters
- **TrackedMessages**: Store all forwarded messages

## 📁 Project Structure

```
yahya-userbot/
├── bot.py              # Main bot application
├── config.py           # Configuration settings
├── db.py              # Database models and operations
├── handlers.py        # Command handlers
├── filters.py         # Message filtering logic
├── requirements.txt   # Python dependencies
├── .env.example      # Environment variables template
├── README.md         # This file
└── session/          # Session files (auto-created)
```

## 🔐 Security Notes

- **Session Security**: Session files are stored in the `session/` folder
- **Environment Variables**: API credentials are stored in `.env` file
- **Database**: SQLite database stores all tracking data locally
- **Privacy**: Only monitors users you explicitly add as targets

## 🐛 Troubleshooting

### Common Issues

**1. "API_ID is required" Error**
- Make sure you've created a `.env` file with your API credentials
- Check that your API_ID is a number without quotes

**2. "SessionPasswordNeededError"**
- You have 2FA enabled on your Telegram account
- Enter your 2FA password when prompted

**3. "Could not find user @username"**
- Make sure the username is correct and exists
- The user must be accessible to your account

**4. "Failed to join the group"**
- Check that the group link is valid and not expired
- Make sure you have permission to join the group

### Debug Mode

Enable debug mode in `config.py`:
```python
DEBUG = True
```

This will show detailed logs of all operations.

## 🔄 Updates and Maintenance

### Database Schema Updates
The bot automatically creates/updates database tables on startup.

### Session Management
- Session files are automatically managed
- Delete files in `session/` folder to reset login

### Data Backup
- Database: `yahya.db`
- Session: `session/` folder
- Export data regularly using `/export` command

## 📊 Performance

- **Real-time Monitoring**: Messages are forwarded within seconds
- **Database Efficiency**: SQLite with proper indexing
- **Memory Usage**: Optimized for long-running operation
- **Error Recovery**: Automatic reconnection and error handling

## 🤝 Contributing

This is a production-grade userbot designed for personal use. Ensure you comply with Telegram's Terms of Service and local laws when using this software.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the debug logs
3. Ensure all dependencies are properly installed
4. Verify your API credentials are correct

## 🎯 Use Cases

- **Crypto Trading**: Monitor specific traders in crypto groups
- **News Monitoring**: Track journalists or news sources
- **Community Management**: Monitor key members in large groups
- **Research**: Collect data from specific users over time

## ⚠️ Important Notes

- This is a **UserBot**, not a regular bot - it uses your personal Telegram account
- Always comply with Telegram's Terms of Service
- Use responsibly and respect others' privacy
- The bot logs all activity for debugging purposes
- Regular backups of your database are recommended

---

**Ready to monitor your targets? Let's get started!** 🚀

```bash
python bot.py
```

*"Yahya must be so robust that I can just plug in my real account and never lose a single target message again."* ✅