#!/usr/bin/env python3
"""
Setup script for Playwright browsers.
Run this script to install the required browsers for web scraping.
"""

import subprocess
import sys
import os

def install_playwright_browsers():
    """Install Playwright browsers."""
    print("🔧 Installing Playwright browsers...")
    
    try:
        # Install Playwright browsers
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Playwright browsers installed successfully!")
            print("📝 You can now run the Good Eats MVP with web scraping capabilities.")
        else:
            print(f"❌ Failed to install Playwright browsers: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing Playwright browsers: {e}")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🚀 Good Eats MVP Setup")
    print("=" * 40)
    
    # Check if Playwright is installed
    try:
        import playwright
        print("✅ Playwright is installed")
    except ImportError:
        print("❌ Playwright is not installed. Please install it first:")
        print("   pip install playwright")
        return False
    
    # Install browsers
    if install_playwright_browsers():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Set up your API keys in .env file:")
        print("   OPENAI_API_KEY=your_openai_api_key_here")
        print("   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here")
        print("2. Run the application:")
        print("   python main.py")
        print("3. Open the web interface:")
        print("   http://localhost:8000/static/index.html")
        return True
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 