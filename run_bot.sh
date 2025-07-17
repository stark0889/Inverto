#!/bin/bash

# PDF Processing Telegram Bot Launch Script

echo "🤖 PDF Processing Bot - Starting..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if BOT_TOKEN is set
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN environment variable is not set!"
    echo ""
    echo "Please set your bot token:"
    echo "   export BOT_TOKEN='your_bot_token_here'"
    echo ""
    echo "To get a bot token:"
    echo "1. Message @BotFather on Telegram"
    echo "2. Send /newbot and follow the instructions"
    echo "3. Copy the token and set it as an environment variable"
    exit 1
fi

# Run the bot
echo "✅ Starting PDF Processing Bot..."
echo "📋 Bot Token: ${BOT_TOKEN:0:10}..."
echo "🔄 Press Ctrl+C to stop the bot"
echo ""

python3 main.py