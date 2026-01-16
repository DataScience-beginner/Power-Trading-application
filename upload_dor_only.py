#!/usr/bin/env python3
"""
Upload ONLY DOR files to Railway PostgreSQL
This creates the 5 clean clients first, then SCH files can link to them.
"""

import requests
import os
from pathlib import Path
import time
from datetime import datetime

RAILWAY_URL = "https://power-trading-application-production.up.railway.app"

def upload_dor_files():
    """Upload only DOR files"""
    
    mock_reports_dir = Path("Data/mock_reports")
    if not mock_reports_dir.exists():
        print(f"❌ Mock reports directory not found: {mock_reports_dir}")
        return False
    
    # Find all DOR files (both .xls and .xlsx)
    dor_files = list(mock_reports_dir.glob("*DOR*.xls*"))
    
    total_files = len(dor_files)
    print(f"📁 Found {total_files} DOR files to upload\n")
    
    success_count = 0
    failed_count = 0
    failed_files = []
    start_time = time.time()
    
    for idx, file_path in enumerate(dor_files, 1):
        try:
            with open(file_path, 'rb') as f:
                files_data = {'file': (file_path.name, f, 'application/vnd.ms-excel')}
                
                response = requests.post(
                    f"{RAILWAY_URL}/api/upload",
                    files=files_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    success_count += 1
                    if idx % 50 == 0 or idx == total_files:
                        elapsed = time.time() - start_time
                        avg_time = elapsed / idx if idx > 0 else 0
                        remaining = (total_files - idx) * avg_time
                        print(f"✅ Progress: {idx}/{total_files} ({idx*100//total_files}%) - "
                              f"Success: {success_count}, Failed: {failed_count} - "
                              f"ETA: {int(remaining/60)}m {int(remaining%60)}s")
                else:
                    failed_count += 1
                    failed_files.append((file_path.name, response.status_code, response.text[:100]))
                    print(f"❌ Failed: {file_path.name} ({response.status_code})")
                    
        except Exception as e:
            failed_count += 1
            failed_files.append((file_path.name, "Exception", str(e)[:100]))
            print(f"❌ Error uploading {file_path.name}: {e}")
    
    elapsed_time = time.time() - start_time
    
    print(f"\n{'='*70}")
    print(f"✅ DOR Upload Complete!")
    print(f"{'='*70}")
    print(f"Success: {success_count}/{total_files}")
    print(f"Failed: {failed_count}")
    print(f"Time: {int(elapsed_time/60)}m {int(elapsed_time%60)}s")
    
    if failed_files:
        print(f"\n❌ Failed files:")
        for fname, status, msg in failed_files[:10]:
            print(f"   {fname}: {status} - {msg}")
    
    # Check clients created
    print(f"\n{'='*70}")
    print(f"Checking clients created...")
    print(f"{'='*70}")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/api/clients", timeout=10)
        if response.status_code == 200:
            clients = response.json()
            client_list = clients.get('clients', [])
            print(f"\n✅ Found {len(client_list)} clients:\n")
            
            for client in client_list:
                print(f"   ID: {client['id']}")
                print(f"   Name: {client['entity_name']}")
                print(f"   Entity ID: {client['entity_id']}")
                portfolios = client.get('portfolios', [])
                print(f"   Portfolios: {len(portfolios)}")
                
                # Show portfolio details
                for portfolio in portfolios:
                    files_count = len(portfolio.get('daily_files', []))
                    print(f"      - {portfolio['portfolio_code']}: {files_count} files")
                print()
    except Exception as e:
        print(f"❌ Error fetching clients: {e}")
    
    return failed_count == 0

if __name__ == "__main__":
    print("\n╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║         Upload DOR Files Only - Create Clean Clients             ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝\n")
    
    upload_dor_files()
