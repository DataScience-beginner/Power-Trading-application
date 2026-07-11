"""
Fast bulk upload of mock reports to Railway PostgreSQL
Uploads files in batches with progress tracking
"""
import requests
from pathlib import Path
import time
import sys

RAILWAY_URL = "https://power-trading-application-production.up.railway.app"
UPLOAD_ENDPOINT = f"{RAILWAY_URL}/api/upload"

def upload_file(filepath):
    """Upload a single file"""
    try:
        with open(filepath, 'rb') as f:
            files = {'file': (filepath.name, f)}
            response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=90)
            
            if response.status_code == 200:
                return True, "Success"
            else:
                error = response.text[:100] if response.text else f"HTTP {response.status_code}"
                return False, error
    except Exception as e:
        return False, str(e)[:100]

def main():
    mock_dir = Path("Data/mock_reports_final")  # Use final proper mocks with 5 clients
    
    if not mock_dir.exists():
        print("❌ Mock reports directory not found!")
        print("   Run: python generate_proper_mock_data.py")
        sys.exit(1)
    
    # Get all Excel files, sorted by name
    files = sorted(mock_dir.glob("*.xlsx"))
    total = len(files)
    
    print(f"{'='*70}")
    print(f"🚀 UPLOADING {total} FILES TO RAILWAY POSTGRESQL")
    print(f"{'='*70}")
    print(f"Target: {RAILWAY_URL}\n")
    
    success_count = 0
    failed_count = 0
    failed_files = []
    
    start_time = time.time()
    
    for i, filepath in enumerate(files, 1):
        # Progress indicator
        percent = (i / total) * 100
        bar_length = 40
        filled = int(bar_length * i / total)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\r[{bar}] {percent:5.1f}% ({i}/{total})", end='', flush=True)
        
        success, message = upload_file(filepath)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
            failed_files.append((filepath.name, message))
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.3)
    
    elapsed = time.time() - start_time
    
    # Final results
    print(f"\n\n{'='*70}")
    print(f"📊 UPLOAD COMPLETE")
    print(f"{'='*70}")
    print(f"✅ Success: {success_count}/{total}")
    print(f"❌ Failed:  {failed_count}/{total}")
    print(f"⏱️  Time:    {elapsed:.1f} seconds")
    print(f"{'='*70}\n")
    
    if failed_files:
        print("Failed files:")
        for filename, error in failed_files[:10]:  # Show first 10 failures
            print(f"  • {filename}: {error}")
        if len(failed_files) > 10:
            print(f"  ... and {len(failed_files) - 10} more")
    
    if success_count > 0:
        print(f"\n🎉 SUCCESS! {success_count} files uploaded to PostgreSQL")
        print(f"\n📊 Next: View your dashboard at {RAILWAY_URL}")
        print(f"💡 Tip: Energy schedules will auto-calculate for matching DOR+SCH pairs\n")
    
    sys.exit(0 if failed_count == 0 else 1)

if __name__ == "__main__":
    main()
