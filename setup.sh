#!/bin/bash

# PDF Processing Telegram Bot Setup Script

echo "🤖 PDF Processing Bot - Setup Script"
echo "====================================="

# Check if we're running on a supported system
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python version: $python_version"

# Install system dependencies (Ubuntu/Debian)
if command -v apt-get &> /dev/null; then
    echo "📦 Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y python3-venv python3-pip poppler-utils
    echo "✅ System dependencies installed"
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment and install Python dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# Run tests
echo "🧪 Running dependency tests..."
python3 test_bot.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Get a bot token from @BotFather on Telegram"
echo "2. Set the environment variable: export BOT_TOKEN='your_bot_token_here'"
echo "3. Run the bot: ./run_bot.sh"
echo ""
echo "For more information, see README.md"