#!/usr/bin/env python3
"""
Upload 15 Days of Mock Data to Railway
======================================

Uploads the generated 15-day mock data in the correct order:
1. Upload all DOR files first (creates clients)
2. Upload all SCH files (links to existing clients)

This ensures proper pairing for energy schedule calculations.
"""

import requests
import time
from pathlib import Path
from datetime import datetime

# Railway URL
RAILWAY_URL = "https://power-trading-application-production.up.railway.app"

# Mock data directory
DATA_DIR = Path("Data/mock_reports_15days")


def upload_files_by_type(file_pattern: str, description: str):
    """Upload files matching pattern"""
    
    if not DATA_DIR.exists():
        print(f"❌ Directory not found: {DATA_DIR}")
        return False
    
    # Find matching files
    files = sorted(list(DATA_DIR.glob(f"*{file_pattern}*.xlsx")))
    
    total_files = len(files)
    if total_files == 0:
        print(f"❌ No files found matching: *{file_pattern}*.xlsx")
        return False
    
    print(f"\n{'='*70}")
    print(f"  Uploading {description}")
    print(f"{'='*70}\n")
    print(f"📁 Found {total_files} files\n")
    
    success_count = 0
    failed_count = 0
    failed_files = []
    start_time = time.time()
    
    for idx, file_path in enumerate(files, 1):
        try:
            with open(file_path, 'rb') as f:
                files_data = {
                    'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                }
                
                response = requests.post(
                    f"{RAILWAY_URL}/api/upload",
                    files=files_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    success_count += 1
                    if idx % 10 == 0 or idx == total_files:
                        elapsed = time.time() - start_time
                        avg_time = elapsed / idx
                        remaining = (total_files - idx) * avg_time
                        print(f"   ✅ {idx}/{total_files} ({idx*100//total_files}%) - "
                              f"ETA: {int(remaining/60)}m {int(remaining%60)}s")
                else:
                    failed_count += 1
                    failed_files.append((file_path.name, response.status_code))
                    print(f"   ❌ {file_path.name[:50]} ({response.status_code})")
                    
        except Exception as e:
            failed_count += 1
            failed_files.append((file_path.name, str(e)))
            print(f"   ❌ {file_path.name[:50]} - Error: {str(e)[:30]}")
    
    elapsed_time = time.time() - start_time
    
    print(f"\n{'='*70}")
    print(f"  Upload Summary: {description}")
    print(f"{'='*70}")
    print(f"✅ Success: {success_count}/{total_files}")
    print(f"❌ Failed: {failed_count}")
    print(f"⏱️  Time: {int(elapsed_time/60)}m {int(elapsed_time%60)}s")
    
    if failed_files:
        print(f"\nFailed Files:")
        for filename, error in failed_files[:10]:  # Show first 10
            print(f"   - {filename}: {error}")
        if len(failed_files) > 10:
            print(f"   ... and {len(failed_files) - 10} more")
    
    print()
    return failed_count == 0


def check_health():
    """Check Railway health"""
    print("\n" + "="*70)
    print("  Railway Health Check")
    print("="*70 + "\n")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Railway is healthy")
            data = response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Railway: {e}")
        return False


def verify_upload():
    """Verify uploaded data"""
    print("\n" + "="*70)
    print("  Verification")
    print("="*70 + "\n")
    
    try:
        # Check clients
        response = requests.get(f"{RAILWAY_URL}/api/clients", timeout=10)
        if response.status_code == 200:
            clients = response.json()
            print(f"✅ Clients: {len(clients)}")
            for client in clients:
                print(f"   - {client['entity_name']}")
        
        print()
        
        # Check files
        response = requests.get(f"{RAILWAY_URL}/api/files?limit=1000", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            print(f"✅ Total Files: {total}")
            
            if 'files' in data:
                dor_count = sum(1 for f in data['files'] if 'DOR' in f.get('report_type', ''))
                sch_count = sum(1 for f in data['files'] if 'SCH' in f.get('report_type', ''))
                print(f"   - DOR Files: {dor_count}")
                print(f"   - SCH Files: {sch_count}")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def main():
    """Main upload workflow"""
    
    print("\n╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║         Upload 15 Days of Mock Data to Railway                   ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    
    # Health check
    if not check_health():
        print("\n❌ Railway not accessible. Aborting.")
        return
    
    # Upload DOR files first
    print("\n🔵 STEP 1: Upload DOR Files (Creates Clients)")
    if not upload_files_by_type("DOR", "Daily Obligation Reports"):
        print("\n⚠️  DOR upload had failures. Continue with SCH? (y/n): ", end="")
        if input().lower() != 'y':
            return
    
    # Small delay
    print("\n⏸️  Waiting 5 seconds before SCH upload...")
    time.sleep(5)
    
    # Upload SCH files
    print("\n🟢 STEP 2: Upload SCH Files (Links to Existing Clients)")
    upload_files_by_type("SCH", "Scheduling Reports")
    
    # Verify
    verify_upload()
    
    print("\n" + "="*70)
    print("  Upload Complete!")
    print("="*70)
    print("\nNext Steps:")
    print("  1. Check dashboard: " + RAILWAY_URL)
    print("  2. Verify energy schedule dropdown shows days > 0")
    print("  3. Test calculations")
    print()


if __name__ == "__main__":
    main()
