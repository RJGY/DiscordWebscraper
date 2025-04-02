# Discord Message Tracker

A Discord bot that monitors specific users in a channel and forwards their messages to dedicated tracking channels. Perfect for keeping tabs on important users in busy servers.

## Features

- **Automated Monitoring**: Periodically checks for new messages from specific users
- **Dedicated Tracking**: Forwards messages to separate channels for each monitored user
- **Message Links**: Includes links to the original messages for easy navigation
- **Attachment Indicators**: Shows when messages contain images or attachments 
- **Manual Fetch**: Use the `!fetch` command to manually trigger message retrieval
- **Embed Formatting**: Displays messages in clean, organized embeds with user avatars
- **Long Message Handling**: Splits longer content into multiple embeds

## Setup

### Requirements
- Python 3.8+ 
- discord.py library
- A Discord bot token
- A Discord user authorization token

### Environment Variables
Create a `.env` file

```
VIEW_CHANNEL_ID=123456789 # ID of the channel to monitor
VIEW_SERVER_ID=123456789 # ID of the server containing the monitored channel
VIEW_USER_IDS=111,222,333 # Comma-separated list of user IDs to monitor
SEND_CHANNEL_IDS=444,555,666 # Comma-separated list of channel IDs where messages will be sent
AUTH_TOKEN=your_auth_token # Your Discord user authorization token
BOT_TOKEN=your_bot_token # Your Discord bot token
```

**Note**: The number of user IDs must match the number of channel IDs.

### Installation
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your environment variables
4. Run the bot: `python main.py`

## Commands

- `!fetch` - Manually trigger message retrieval

## Disclaimer

This bot uses user authorization tokens which is against Discord's Terms of Service. Use at your own risk.

## Upcoming Features

- [ ] Multi-channel monitoring
- [ ] Dynamic user and channel configuration
- [ ] Improved attachment handling
- [ ] Better code structure to reduce duplication
- [ ] User-friendly error messages