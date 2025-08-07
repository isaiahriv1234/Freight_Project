#!/usr/bin/env python3
"""
Setup EasyPost Integration
Installs required packages and tests API connection
"""

import subprocess
import sys

def install_packages():
    """Install required packages"""
    packages = ["easypost", "python-dotenv"]
    
    for package in packages:
        print(f"📦 Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    return True

def test_api_connection():
    """Test EasyPost API connection"""
    print("🔗 Testing API connection...")
    try:
        import easypost
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('EASYPOST_API_KEY')
        if not api_key:
            print("❌ API key not found in .env file")
            return False
            
        easypost.api_key = api_key
        
        # Test with a simple address verification
        address = easypost.Address.create(
            name="Cal Poly SLO",
            street1="1 Grand Ave",
            city="San Luis Obispo",
            state="CA",
            zip="93407",
            country="US"
        )
        
        print("✅ API connection successful")
        print(f"📍 Test address verified: {address.street1}, {address.city}")
        return True
        
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 EASYPOST INTEGRATION SETUP")
    print("=" * 40)
    
    # Install packages
    if install_packages():
        # Test API connection
        if test_api_connection():
            print("\n✅ SETUP COMPLETE!")
            print("🎯 You can now run:")
            print("   python procurement_analysis.py")
            print("   python easypost_shipping_optimizer.py")
        else:
            print("\n⚠️  Installation complete but API test failed")
            print("Check your API key and internet connection")
    else:
        print("\n❌ Setup failed")
        print("Try running: pip install easypost")

if __name__ == "__main__":
    main()