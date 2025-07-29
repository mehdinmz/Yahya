# 🎯 Yahya UserBot - Telegram Group Message Hunter 🤖

A production-grade Python Telegram UserBot built with **Telethon** for real-time message monitoring, filtering, and forwarding. Monitor specific users across multiple groups with **individual filtering capabilities** for each target.

## 🚀 Features

- **🎯 Individual Target Monitoring**: Monitor specific users across multiple Telegram groups with personalized filters
- **⚡ Real-time Forwarding**: Instantly forward matching messages to your private chat
- **🔍 Per-Target Advanced Filters**: Set unique filters (keywords, language, media types) for each target individually
- **💾 SQLite Database**: Store all tracked messages with full details and filter configurations
- **📊 Data Export**: Export all tracked messages as CSV files
- **🛡️ Robust Error Handling**: Graceful handling of all edge cases
- **🔐 Session Management**: Secure session storage and management
- **🎛️ Granular Control**: Each target can have completely different monitoring criteria

## 📋 Requirements

- Python 3.8+
- Telegram API credentials (API_ID and API_HASH)
- Your personal Telegram account

## 🛠️ Installation

## 🧰 Installing & Running Yahya

1. **Clone the repository**
   ```bash
   git clone https://github.com/OS-Jalal/Yahya.git
   cd Yahya
   ```
2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   ```
3. **Activate the virtual environment**
   
   **Windows:**
   ```bash
   .venv\Scripts\activate
   ```
   **Mac/Linux:**
   ```bash
   source .venv/bin/activate
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Get Telegram API credentials:**
   - Go to https://my.telegram.org/apps
   - Create a new application
   - Note down your `API_ID` and `API_HASH`

6. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your API credentials:
   ```bash
   API_ID=your_api_id_here
   API_HASH=your_api_hash_here
   ```

## 🎮 Usage

### Start the Bot

```bash
python main.py
```

On first run, you'll be prompted to:
1. Enter your phone number
2. Enter the verification code sent to your Telegram
3. Enter your 2FA password (if enabled)

### Available Commands

#### 📋 Target Management
- `/start` - Register your account and show welcome message
- `/newtarget @username group_link` - Add a new target to monitor
- `/viewtargets` - View all your active targets with filter status
- `/removetarget @username` - Remove a target from monitoring

#### 🔧 Individual Filter Management (Per Target)
- `/setfilter @username [parameters]` - Set filters for a specific target
- `/viewfilter @username` - View filters for a specific target
- `/clearfilter @username` - Clear all filters for a specific target

#### 📊 Data Management
- `/export` - Export all tracked messages as CSV file
- `/help` - Show command reference

### Command Examples

**Add a new target:**
```
/newtarget @johndoe https://t.me/+AbCdEfGhIjKlMnOp
```

**Set individual filters for different targets:**
```
/setfilter @johndoe keywords:bitcoin,crypto language:en
/setfilter @alice media:photo,video
/setfilter @bob keywords:important language:fa media:text
```

**View filters for a specific target:**
```
/viewfilter @johndoe
```

**Clear filters for a target:**
```
/clearfilter @alice
```

**Remove a target:**
```
/removetarget @johndoe
```

## 🔧 Advanced Individual Filtering

### Per-Target Keywords Filter
Set different keywords for each target:
```
/setfilter @trader1 keywords:bitcoin,ethereum,trading
/setfilter @news_bot keywords:breaking,urgent,alert
/setfilter @analyst keywords:analysis,prediction,forecast
```

### Per-Target Language Filter
Filter messages by language for each target individually:
```
/setfilter @english_user language:en
/setfilter @persian_user language:fa
/setfilter @arabic_user language:ar
```
Supported languages: `en`, `fa`, `ar`, `fr`, `de`, `es`, `it`, `ru`, `zh`, `ja`, `ko`

### Per-Target Media Type Filter
Set different media preferences for each target:
```
/setfilter @photo_user media:photo,image
/setfilter @video_creator media:video
/setfilter @text_only media:text
```
Supported types: `text`, `photo`, `video`, `audio`, `image`, `document`, `media`

### Combined Per-Target Filters
Each target can have multiple filter types:
```
/setfilter @vip_user keywords:important,urgent language:en media:text,photo
/setfilter @crypto_expert keywords:bitcoin,analysis language:en media:text
/setfilter @media_channel media:photo,video
```

### Managing Individual Filters
```
# View all targets and their filter status
/viewtargets

# Check specific target's filters
/viewfilter @username

# Remove all filters from a target (monitor everything)
/clearfilter @username
```

## 🗃️ Database Schema

The bot uses SQLite with the following optimized tables:

- **Users**: Store user information
- **Targets**: Store target monitoring configuration **with individual filters**
- **TrackedMessages**: Store all forwarded messages

### New Schema Benefits:
- **Individual Control**: Each target has its own filter settings
- **Better Performance**: Simplified schema with fewer joins
- **Easier Management**: Filter settings stored directly with targets

## 📁 Project Structure

```
yahya-userbot/
├── main.py            # Main bot application
├── config.py          # Configuration settings
├── db.py             # Database models and operations
├── handlers.py       # Command handlers
├── filters.py        # Message filtering logic
├── requirements.txt  # Python dependencies
├── .env.example     # Environment variables template
├── README.md        # This file
└── session/         # Session files (auto-created)
```

## 🎯 Real-World Use Cases

### Crypto Trading Scenario
```bash
# Monitor different types of crypto users with specific filters
/newtarget @whale_trader https://t.me/cryptogroup1
/setfilter @whale_trader keywords:buy,sell,pump language:en media:text

/newtarget @technical_analyst https://t.me/cryptogroup2  
/setfilter @technical_analyst keywords:analysis,chart,resistance language:en

/newtarget @news_aggregator https://t.me/cryptonews
/setfilter @news_aggregator keywords:breaking,news media:text,photo
```

### News Monitoring Scenario
```bash
# Monitor journalists with different language preferences
/newtarget @english_reporter https://t.me/newsgroup
/setfilter @english_reporter language:en media:text,photo

/newtarget @persian_journalist https://t.me/persian_news
/setfilter @persian_journalist language:fa keywords:اخبار,مهم

/newtarget @breaking_news https://t.me/alerts
/setfilter @breaking_news keywords:breaking,urgent,alert
```

### Community Management Scenario
```bash
# Monitor key community members with different criteria
/newtarget @community_leader https://t.me/large_group
/setfilter @community_leader keywords:announcement,important

/newtarget @tech_expert https://t.me/tech_group
/setfilter @tech_expert keywords:tutorial,guide,help media:text,document

/newtarget @media_creator https://t.me/content_group
/setfilter @media_creator media:photo,video
```

## 🔐 Security Notes

- **Session Security**: Session files are stored in the `session/` folder
- **Environment Variables**: API credentials are stored in `.env` file
- **Database**: SQLite database stores all tracking data locally
- **Privacy**: Only monitors users you explicitly add as targets
- **Individual Privacy**: Each target's filters are isolated and private

## 🐛 Troubleshooting

### Common Issues

**1. "API_ID is required" Error**
- Make sure you've created a `.env` file with your API credentials
- Check that your API_ID is a number without quotes

**2. "SessionPasswordNeededError"**
- You have 2FA enabled on your Telegram account
- Enter your 2FA password when prompted

**3. "Target @username not found in your active targets"**
- Make sure you've added the target using `/newtarget` first
- Check the username spelling

**4. "Failed to join the group"**
- Check that the group link is valid and not expired
- Make sure you have permission to join the group

**5. Filter Not Working**
- Use `/viewfilter @username` to check current filters
- Remember filters are per-target, not global
- Use `/clearfilter @username` to reset and try again

## 🔄 Updates and Maintenance

### Database Schema Updates
The bot automatically creates/updates database tables on startup. The new schema supports individual target filters.

### Session Management
- Session files are automatically managed
- Delete files in `session/` folder to reset login

### Data Backup
- Database: `yahya.db`
- Session: `session/` folder
- Export data regularly using `/export` command

### Migration from Old Version
If upgrading from a previous version:
1. The new schema will be automatically created
2. Old global filters will need to be reconfigured per target
3. Use `/viewtargets` to see all targets and their filter status

## 📊 Performance

- **Real-time Monitoring**: Messages are forwarded within seconds
- **Individual Processing**: Each target is processed with its own filters
- **Database Efficiency**: Optimized SQLite schema with proper indexing
- **Memory Usage**: Optimized for long-running operation with multiple targets
- **Error Recovery**: Automatic reconnection and error handling per target

## 🆕 What's New in v2.1

### Major Updates:
- **🎯 Individual Target Filters**: Each target now has its own filter settings
- **🧹 Code Cleanup**: Removed all debug statements and improved English comments
- **📋 New Commands**: Added `/clearfilter` command for better filter management
- **🔧 Enhanced UI**: Better status display in `/viewtargets`
- **⚡ Performance**: Simplified database schema for better performance

### Breaking Changes:
- **Filter Commands Changed**: Now require target username (e.g., `/setfilter @username`)
- **Database Schema**: Updated to support per-target filters
- **Command Structure**: More intuitive command structure with target-specific operations

## 🤝 Contributing

This is a production-grade userbot designed for personal use. Ensure you comply with Telegram's Terms of Service and local laws when using this software.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Use `/help` command to see all available commands
3. Ensure all dependencies are properly installed
4. Verify your API credentials are correct

## ⚠️ Important Notes

- This is a **UserBot**, not a regular bot - it uses your personal Telegram account
- Always comply with Telegram's Terms of Service
- Use responsibly and respect others' privacy
- Each target can have completely different monitoring settings
- Regular backups of your database are recommended
- The new individual filter system provides much more control and flexibility

---

**Ready to monitor your targets with individual precision?** 🚀

```bash
python main.py
```

*"Monitor each target exactly how you want - because one size doesn't fit all!"* ✨

### Quick Start Example:
```bash
# Add targets
/newtarget @crypto_whale https://t.me/cryptogroup
/newtarget @news_bot https://t.me/newsgroup

# Set individual filters
/setfilter @crypto_whale keywords:bitcoin,buy,sell language:en
/setfilter @news_bot keywords:breaking,urgent media:text,photo

# Monitor and enjoy! 🎯
```