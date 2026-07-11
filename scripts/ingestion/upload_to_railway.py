"""
Upload mock reports to Railway deployment
Run this to populate your Railway PostgreSQL database
"""
import requests
from pathlib import Path
import time

# Your Railway app URL
RAILWAY_URL = "https://power-trading-application-production.up.railway.app"
# Or use: power-trading-application-production-up.railway.app

def upload_file(filepath):
    """Upload a single file to Railway API"""
    url = f"{RAILWAY_URL}/api/upload"
    
    with open(filepath, 'rb') as f:
        files = {'file': (filepath.name, f, 'application/vnd.ms-excel')}
        
        try:
            response = requests.post(url, files=files, timeout=30)
            if response.status_code == 200:
                print(f"✅ {filepath.name}")
                return True
            else:
                print(f"❌ {filepath.name} - {response.status_code}: {response.text[:100]}")
                return False
        except Exception as e:
            print(f"❌ {filepath.name} - Error: {e}")
            return False

def main():
    """Upload all mock reports"""
    mock_dir = Path("Data/mock_reports")
    
    if not mock_dir.exists():
        print("❌ Mock reports directory not found!")
        print("   Run: python generate_mock_reports.py")
        return
    
    # Get all Excel files
    files = sorted(mock_dir.glob("*.xls*"))
    
    print(f"📤 Uploading {len(files)} files to Railway...")
    print(f"🌐 Target: {RAILWAY_URL}\n")
    
    success = 0
    failed = 0
    
    for filepath in files:
        if upload_file(filepath):
            success += 1
        else:
            failed += 1
        time.sleep(0.5)  # Avoid overwhelming the server
    
    print(f"\n{'='*60}")
    print(f"✅ Uploaded: {success}")
    print(f"❌ Failed: {failed}")
    print(f"{'='*60}")
    
    if success > 0:
        print(f"\n🎉 Visit your app: {RAILWAY_URL}")
        print("   Data should now be visible in the dashboard!")

if __name__ == "__main__":
    main()
