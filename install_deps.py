#!/usr/bin/env python3
"""
Dependency installation script for PDF processing bot
Handles system-level dependencies like poppler-utils
"""

import os
import sys
import subprocess
import platform

def run_command(command):
    """Run a system command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def install_poppler():
    """Install poppler-utils based on the operating system"""
    system = platform.system().lower()
    
    print(f"Detected system: {system}")
    
    if system == "linux":
        # Try different package managers
        managers = [
            ("apt-get", "sudo apt-get update && sudo apt-get install -y poppler-utils"),
            ("yum", "sudo yum install -y poppler-utils"),
            ("dnf", "sudo dnf install -y poppler-utils"),
            ("pacman", "sudo pacman -S --noconfirm poppler"),
        ]
        
        for manager, command in managers:
            success, _, _ = run_command(f"which {manager}")
            if success:
                print(f"Installing poppler-utils using {manager}...")
                success, stdout, stderr = run_command(command)
                if success:
                    print("✅ poppler-utils installed successfully")
                    return True
                else:
                    print(f"❌ Failed to install with {manager}: {stderr}")
        
        print("❌ Could not find a suitable package manager")
        return False
        
    elif system == "darwin":  # macOS
        print("Installing poppler using Homebrew...")
        success, stdout, stderr = run_command("brew install poppler")
        if success:
            print("✅ poppler installed successfully")
            return True
        else:
            print(f"❌ Failed to install poppler: {stderr}")
            print("Please install Homebrew first: https://brew.sh/")
            return False
            
    elif system == "windows":
        print("For Windows, please install poppler manually:")
        print("1. Download from: https://github.com/oschwartz10612/poppler-windows/releases")
        print("2. Extract and add to PATH")
        print("3. Or use conda: conda install -c conda-forge poppler")
        return False
    
    else:
        print(f"Unsupported system: {system}")
        return False

def test_poppler():
    """Test if poppler is installed and working"""
    success, stdout, stderr = run_command("pdftoppm -h")
    return success

def install_python_deps():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    success, stdout, stderr = run_command("pip install -r requirements.txt")
    if success:
        print("✅ Python dependencies installed successfully")
        return True
    else:
        print(f"❌ Failed to install Python dependencies: {stderr}")
        return False

def main():
    """Main installation process"""
    print("🤖 PDF Processing Bot - Dependency Installer\n")
    
    # Check if poppler is already installed
    if test_poppler():
        print("✅ poppler-utils is already installed")
    else:
        print("❌ poppler-utils not found, attempting to install...")
        if not install_poppler():
            print("\n⚠️  Manual installation required for poppler-utils")
            print("The bot may not work without this dependency.")
            print("\nFor cloud platforms:")
            print("- Replit: poppler-utils is usually pre-installed")
            print("- Render: Add 'apt-get install -y poppler-utils' to build command")
            print("- Heroku: Add 'poppler-utils' to Aptfile")
    
    # Install Python dependencies
    if install_python_deps():
        print("\n🎉 Installation completed!")
        print("You can now run the bot with: python main.py")
        print("Don't forget to set your BOT_TOKEN environment variable!")
    else:
        print("\n❌ Installation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()