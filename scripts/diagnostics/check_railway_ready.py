#!/usr/bin/env python3
"""
Quick Railway deployment status check
Run this every 30 seconds to see when Railway is ready
"""

import requests
import time

RAILWAY_URL = "https://power-trading-application-production.up.railway.app"

def check_railway():
    try:
        r = requests.get(f"{RAILWAY_URL}/api/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            timestamp = data.get('timestamp', 'Unknown')
            print(f"✅ Railway is UP (Last updated: {timestamp})")
            return True
        else:
            print(f"⚠️  Railway responded with: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Railway not accessible: {e}")
        return False

if __name__ == "__main__":
    print("Checking Railway deployment status...")
    print("(Run this every 30 seconds until you see a new timestamp)\n")
    
    if check_railway():
        print("\n✅ Railway is ready!")
        print("\nNext step:")
        print("  python final_fix_railway.py")
    else:
        print("\n⏳ Railway is redeploying...")
        print("\nWait 1-2 minutes and run this again:")
        print("  python check_railway_ready.py")
