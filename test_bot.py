#!/usr/bin/env python3
"""
Test script to verify bot dependencies and basic functionality
"""

import os
import sys
import tempfile
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import telegram
        print("✅ python-telegram-bot imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import python-telegram-bot: {e}")
        return False
    
    try:
        from pdf2image import convert_from_path
        print("✅ pdf2image imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pdf2image: {e}")
        return False
    
    try:
        from PIL import Image, ImageOps
        print("✅ Pillow imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Pillow: {e}")
        return False
    
    try:
        import img2pdf
        print("✅ img2pdf imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import img2pdf: {e}")
        return False
    
    return True

def test_environment():
    """Test environment setup"""
    print("\nTesting environment...")
    
    bot_token = os.environ.get("BOT_TOKEN")
    if bot_token:
        print("✅ BOT_TOKEN environment variable is set")
        # Don't print the actual token for security
        print(f"   Token length: {len(bot_token)} characters")
        return True
    else:
        print("❌ BOT_TOKEN environment variable is not set")
        print("   Please set it with: export BOT_TOKEN='your_bot_token_here'")
        return False

def test_file_operations():
    """Test basic file operations"""
    print("\nTesting file operations...")
    
    try:
        # Test temporary directory creation
        temp_dir = tempfile.mkdtemp()
        print(f"✅ Temporary directory created: {temp_dir}")
        
        # Test file creation
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        print("✅ File creation successful")
        
        # Test file removal
        os.remove(test_file)
        os.rmdir(temp_dir)
        print("✅ File cleanup successful")
        
        return True
    except Exception as e:
        print(f"❌ File operations failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 PDF Processing Bot - Dependency Test\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Test", test_environment),
        ("File Operations Test", test_file_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name}")
        print('='*50)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed! The bot should work correctly.")
        print("\nTo start the bot, run:")
        print("python main.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues before running the bot.")
        
        if not os.environ.get("BOT_TOKEN"):
            print("\n💡 Quick fix for BOT_TOKEN:")
            print("1. Get a bot token from @BotFather on Telegram")
            print("2. Set the environment variable:")
            print("   export BOT_TOKEN='your_bot_token_here'")

if __name__ == "__main__":
    main()