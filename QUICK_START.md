# 🚀 Quick Start Guide

Get your PDF Processing Telegram Bot up and running in minutes!

## Step 1: Get a Bot Token

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Copy the bot token (it looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Set Up the Bot

### Option A: Automatic Setup (Recommended)
```bash
# Run the setup script
./setup.sh
```

### Option B: Manual Setup
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip poppler-utils

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## Step 3: Set Your Bot Token

```bash
export BOT_TOKEN='your_bot_token_here'
```

## Step 4: Run the Bot

```bash
# Using the launch script
./run_bot.sh

# Or manually
source venv/bin/activate
python3 main.py
```

## Step 5: Test Your Bot

1. Find your bot on Telegram using the username you chose
2. Send `/start` to see the welcome message
3. Upload a PDF file
4. Try the commands:
   - `/invert` - Invert colors
   - `/layout_2in1` - 2 pages per sheet
   - `/layout_4in1` - 4 pages per sheet

## 🎉 You're Done!

Your bot is now ready to process PDF files!

## 🔧 Troubleshooting

- **Bot not responding**: Check if `BOT_TOKEN` is set correctly
- **Import errors**: Run `python3 test_bot.py` to verify dependencies
- **PDF processing fails**: Ensure `poppler-utils` is installed

## 📚 More Information

- See [README.md](README.md) for detailed documentation
- Check [main.py](main.py) for the bot source code
- Run `python3 test_bot.py` to test your setup