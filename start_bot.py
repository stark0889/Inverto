#!/usr/bin/env python3
"""
Simple script to start the PDF Processing Bot with the configured token
"""

import os
import sys

# Set the bot token
os.environ['BOT_TOKEN'] = '7598007399:AAG8Zs_E8iifjnUGdyRWqpfcQKHyQV4tIkw'

# Import and run the main bot
if __name__ == "__main__":
    try:
        from main import main
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)