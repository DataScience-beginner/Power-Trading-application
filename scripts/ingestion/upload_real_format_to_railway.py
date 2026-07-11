#!/usr/bin/env python3
"""
Upload real-format mock files to Railway
These files have proper Excel structure that the parser expects
"""

import requests
from pathlib import Path
import time

RAILWAY_URL = "https://power-trading-application-production.up.railway.app"

def upload_files():
    """Upload all real format files to Railway"""
    
    mock_dir = Path("Data/mock_reports_real_format")
    if not mock_dir.exists():
        print(f"❌ Directory not found: {mock_dir}")
        return
    
    # Get all DOR files first
    dor_files = list(mock_dir.glob("*DOR*.xlsx"))
    sch_files = list(mock_dir.glob("*SCH*.xlsx"))
    
    print(f"\n{'='*70}")
    print(f"Found {len(dor_files)} DOR files and {len(sch_files)} SCH files")
    print(f"{'='*70}\n")
    
    # Upload DOR files first
    print("📤 Uploading DOR files...\n")
    success = 0
    failed = 0
    failed_details = []
    start_time = time.time()
    
    for idx, file_path in enumerate(dor_files, 1):
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
                        print(f"   ✅ {idx}/{len(dor_files)} uploaded...")
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
    print(f"✅ DOR Upload Complete!")
    print(f"{'='*70}")
    print(f"Success: {success}/{len(dor_files)}")
    print(f"Failed: {failed}")
    print(f"Time: {int(elapsed/60)}m {int(elapsed%60)}s\n")
    
    if failed_details:
        print("❌ Failed files:")
        for detail in failed_details[:10]:  # Show first 10
            print(f"   {detail}")
        print()
    
    # Check clients created
    print(f"{'='*70}")
    print("Checking clients created...")
    print(f"{'='*70}\n")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/api/clients", timeout=10)
        if response.status_code == 200:
            clients = response.json()
            print(f"✅ Found {len(clients)} clients:\n")
            for client in clients:
                print(f"   {client['entity_name']} (ID: {client['id']}, Entity: {client['entity_id']})")
        else:
            print(f"❌ Failed to fetch clients: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching clients: {e}")
    
    # Now upload SCH files if DOR was successful
    if success > 0 and len(sch_files) > 0:
        print(f"\n{'='*70}")
        print(f"📤 Uploading SCH files...")
        print(f"{'='*70}\n")
        
        sch_success = 0
        sch_failed = 0
        sch_failed_details = []
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
                        sch_success += 1
                        if idx % 10 == 0:
                            print(f"   ✅ {idx}/{len(sch_files)} uploaded...")
                    else:
                        sch_failed += 1
                        error_msg = response.text[:150] if response.text else "No error message"
                        sch_failed_details.append(f"{file_path.name}: {response.status_code} - {error_msg}")
                        print(f"   ❌ Failed: {file_path.name} ({response.status_code})")
                        
            except Exception as e:
                sch_failed += 1
                sch_failed_details.append(f"{file_path.name}: {str(e)}")
                print(f"   ❌ Error: {file_path.name} - {e}")
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*70}")
        print(f"✅ SCH Upload Complete!")
        print(f"{'='*70}")
        print(f"Success: {sch_success}/{len(sch_files)}")
        print(f"Failed: {sch_failed}")
        print(f"Time: {int(elapsed/60)}m {int(elapsed%60)}s\n")
        
        if sch_failed_details:
            print("❌ Failed files:")
            for detail in sch_failed_details[:10]:
                print(f"   {detail}")

if __name__ == "__main__":
    upload_files()
