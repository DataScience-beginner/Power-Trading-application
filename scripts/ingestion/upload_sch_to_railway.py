#!/usr/bin/env python3
"""
Upload SCH files to Railway
"""

import requests
from pathlib import Path
import time

RAILWAY_URL = "https://power-trading-application-production.up.railway.app"

def upload_sch_files():
    """Upload all SCH files to Railway"""
    
    sch_dir = Path("Data/mock_reports_sch")
    if not sch_dir.exists():
        print(f"❌ Directory not found: {sch_dir}")
        return
    
    sch_files = list(sch_dir.glob("*.xlsx"))
    
    print(f"\n{'='*70}")
    print(f"📤 Uploading {len(sch_files)} SCH files to Railway...")
    print(f"{'='*70}\n")
    
    success = 0
    failed = 0
    failed_details = []
    start_time = time.time()
    
    for idx, file_path in enumerate(sch_files, 1):
        try:
            with open(file_path, 'rb') as f:
                files_data = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                
                response = requests.post(
                    f"{RAILWAY_URL}/api/upload",
                    files=files_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    success += 1
                    if idx % 10 == 0:
                        print(f"   ✅ {idx}/{len(sch_files)} uploaded...")
                else:
                    failed += 1
                    error_msg = response.text[:150] if response.text else "No error message"
                    failed_details.append(f"{file_path.name}: {response.status_code} - {error_msg}")
                    print(f"   ❌ Failed: {file_path.name} ({response.status_code})")
                    
        except Exception as e:
            failed += 1
            failed_details.append(f"{file_path.name}: {str(e)}")
            print(f"   ❌ Error: {file_path.name} - {e}")
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*70}")
    print(f"✅ SCH Upload Complete!")
    print(f"{'='*70}")
    print(f"Success: {success}/{len(sch_files)}")
    print(f"Failed: {failed}")
    print(f"Time: {int(elapsed/60)}m {int(elapsed%60)}s\n")
    
    if failed_details:
        print("❌ Failed files (first 10):")
        for detail in failed_details[:10]:
            print(f"   {detail}")
        print()
    
    # Check total files
    print(f"{'='*70}")
    print("Checking total files in database...")
    print(f"{'='*70}\n")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/api/files?limit=200", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('count', 0)
            print(f"✅ Total files in database: {total}")
            print(f"   Expected: 180 (90 DOR + 90 SCH)")
            
            if total >= 180:
                print(f"\n✅ SUCCESS! All files uploaded.")
            else:
                print(f"\n⚠️  Expected 180 files, got {total}")
        else:
            print(f"❌ Failed to fetch files: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching files: {e}")

if __name__ == "__main__":
    upload_sch_files()
