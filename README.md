# reel-responder-bot
A bot designed to respond to all the reels that Iʼve forgotten to reply to that my friends send me.

## 🚀 Features

- **Auto-monitors Instagram DMs** for reel messages
- **Fetches top comments** from each reel using Apify
- **AI-generated replies** using OpenAI (GPT-4o-mini) based on reel comments
- **Prevents duplicate replies** by tracking message history
- **Continuous operation** with configurable polling interval

## 🛠️ Setup

### 1. Clone and Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` with your credentials:

```env
INSTA_USERNAME=your_instagram_username
INSTA_PASSWORD=your_instagram_password
OPENAI_API_KEY=your_openai_api_key
APIFY_KEY=your_apify_key
```

**Where to get API keys:**
- **OpenAI API Key**: https://platform.openai.com/api-keys
- **Apify API Token**: https://console.apify.com/account/integrations

### 3. Run the Bot

```bash
python main.py
```

## 📖 How It Works

1. **Monitors DMs**: Every 10 seconds, the bot checks for new reel messages
2. **Scrapes Comments**: For each new reel, it fetches the top 3 comments using Apify
3. **Generates Reply**: Uses OpenAI (GPT-4o-mini) to create a funny, contextual response
4. **Sends Response**: Automatically replies to the thread and marks the message as seen
5. **Tracks History**: Saves replied message IDs in `store.json` to avoid duplicates

## 🔧 Configuration

You can customize these settings in `main.py`:

- `POLL_INTERVAL`: How often to check for new messages (default: 10 seconds)
- Comment limit in `get_reel_comments()` (default: 3 comments)
- AI prompt in `generate_reply()` to change response style

## 📝 Project Structure

```
reel-responder-bot/
├── main.py              # Main bot logic
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── .gitignore          # Git ignore rules
├── store.json          # Message history (auto-generated)
└── README.md           # This file
```

## ⚠️ Important Notes

- Instagram may flag automated activity - use responsibly

- The bot uses OpenAI's GPT-4o-mini model for cost-effective, fast responses
- `store.json` tracks replied messages - don't delete it unless you want to reset
