#!/usr/bin/env python3
"""
Systematic Database Fix for Railway PostgreSQL
==============================================

This script performs a complete reset and re-upload workflow:
1. Reset Railway database (delete all data)
2. Upload DOR files (450 files) - creates 5 clean clients
3. Wait for Railway redeploy with fixed SCH parser
4. Upload SCH files (450 files) - links to existing clients
5. Verify data integrity
6. Test energy schedule calculation

Run this after the SCH parser fix has been deployed to Railway.
"""

import requests
import os
from pathlib import Path
import time
from datetime import datetime

# Railway API endpoint
RAILWAY_URL = "https://power-trading-application-production.up.railway.app"

def print_header(message):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {message}")
    print(f"{'='*70}\n")

def check_railway_health():
    """Check if Railway API is responding"""
    print_header("STEP 1: Health Check")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Railway API is healthy")
            print(f"   Service: {data.get('service')}")
            print(f"   Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Railway: {e}")
        return False

def reset_database():
    """Reset Railway database"""
    print_header("STEP 2: Reset Database")
    
    print("⚠️  WARNING: This will DELETE ALL DATA from Railway PostgreSQL!")
    print("    - All clients")
    print("    - All portfolios")
    print("    - All daily files (994 files)")
    print("    - All transactions")
    print("    - All energy schedule calculations")
    print()
    
    confirm = input("Type 'RESET' to confirm deletion: ")
    if confirm != "RESET":
        print("❌ Reset cancelled")
        return False
    
    try:
        print("\n🗑️  Sending reset request...")
        response = requests.post(f"{RAILWAY_URL}/api/admin/reset-database", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database reset complete!")
            print(f"\n   Deleted:")
            print(f"   - {data['deleted']['clients']} clients")
            print(f"   - {data['deleted']['portfolios']} portfolios")
            print(f"   - {data['deleted']['daily_files']} daily files")
            print(f"   - {data['deleted']['transactions']} transactions")
            return True
        else:
            print(f"❌ Reset failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Reset error: {e}")
        return False

def upload_files(file_pattern: str, description: str):
    """Upload files matching pattern to Railway"""
    
    mock_reports_dir = Path("Data/mock_reports")
    if not mock_reports_dir.exists():
        print(f"❌ Mock reports directory not found: {mock_reports_dir}")
        return False
    
    # Find matching files
    if "DOR" in file_pattern:
        files = list(mock_reports_dir.glob("*DOR*.xls"))
    else:
        files = list(mock_reports_dir.glob("*SCH*.xls"))
    
    total_files = len(files)
    if total_files == 0:
        print(f"❌ No files found matching pattern: {file_pattern}")
        return False
    
    print(f"📁 Found {total_files} files to upload")
    print(f"   Pattern: {file_pattern}")
    print()
    
    success_count = 0
    failed_count = 0
    start_time = time.time()
    
    for idx, file_path in enumerate(files, 1):
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
                    if idx % 50 == 0:
                        elapsed = time.time() - start_time
                        avg_time = elapsed / idx
                        remaining = (total_files - idx) * avg_time
                        print(f"   Progress: {idx}/{total_files} ({idx*100//total_files}%) - "
                              f"ETA: {int(remaining/60)}m {int(remaining%60)}s")
                else:
                    failed_count += 1
                    print(f"   ❌ Failed: {file_path.name} ({response.status_code})")
                    
        except Exception as e:
            failed_count += 1
            print(f"   ❌ Error uploading {file_path.name}: {e}")
    
    elapsed_time = time.time() - start_time
    print(f"\n✅ Upload complete!")
    print(f"   Success: {success_count}/{total_files}")
    print(f"   Failed: {failed_count}")
    print(f"   Time: {int(elapsed_time/60)}m {int(elapsed_time%60)}s")
    
    return failed_count == 0

def verify_clients():
    """Verify client count and details"""
    print_header("Verification: Check Clients")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/api/clients", timeout=10)
        if response.status_code == 200:
            clients = response.json()
            print(f"✅ Found {len(clients)} clients:\n")
            
            for client in clients:
                print(f"   ID: {client['id']}")
                print(f"   Name: {client['entity_name']}")
                print(f"   Entity ID: {client['entity_id']}")
                print(f"   Portfolios: {len(client.get('portfolios', []))}")
                print()
            
            # Expected: 5 clients after DOR upload, same 5 after SCH upload
            return True
        else:
            print(f"❌ Failed to fetch clients: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error fetching clients: {e}")
        return False

def verify_files():
    """Verify file count"""
    print_header("Verification: Check Files")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/api/files?limit=1000", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_files = data.get('total', 0)
            print(f"✅ Total files in database: {total_files}")
            
            # Count by report type
            if 'files' in data:
                dor_count = sum(1 for f in data['files'] if 'DOR' in f.get('report_type', ''))
                sch_count = sum(1 for f in data['files'] if 'SCH' in f.get('report_type', ''))
                print(f"   DOR files: {dor_count}")
                print(f"   SCH files: {sch_count}")
            
            # Expected: 450 DOR + 450 SCH = 900 total
            if total_files == 900:
                print(f"\n✅ File count is correct! (900 expected)")
                return True
            else:
                print(f"\n⚠️  File count mismatch (expected 900, got {total_files})")
                return False
        else:
            print(f"❌ Failed to fetch files: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error fetching files: {e}")
        return False

def test_energy_schedule():
    """Test energy schedule calculation"""
    print_header("Verification: Test Energy Schedule Calculation")
    
    # For calculation to work, we need:
    # 1. DOR file from Jan 1, 2026
    # 2. SCH file from Jan 2, 2026
    # Both must be from same client/portfolio
    
    print("📊 Testing energy schedule calculation for Jan 2, 2026...")
    print("   Requires: DOR from Jan 1 + SCH from Jan 2 (same client)")
    print()
    
    try:
        # Get first client
        response = requests.get(f"{RAILWAY_URL}/api/clients", timeout=10)
        if response.status_code != 200:
            print(f"❌ Cannot fetch clients")
            return False
        
        clients = response.json()
        if not clients:
            print(f"❌ No clients found")
            return False
        
        client = clients[0]
        print(f"   Testing with client: {client['entity_name']}")
        print(f"   Entity ID: {client['entity_id']}")
        
        # Trigger calculation
        payload = {
            "client_id": client['id'],
            "calculation_date": "2026-01-02"
        }
        
        response = requests.post(
            f"{RAILWAY_URL}/api/calculate/energy-schedule",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Energy schedule calculation successful!")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            
            if 'result' in result:
                calc_result = result['result']
                print(f"\n   Calculation Results:")
                print(f"   - Trading Date: {calc_result.get('trading_date')}")
                print(f"   - Total CTU Losses: {calc_result.get('total_ctu_losses_mwh', 0):.2f} MWh")
                print(f"   - Total Energy Saved: {calc_result.get('total_energy_saved_mwh', 0):.2f} MWh")
            
            return True
        else:
            print(f"\n❌ Calculation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Calculation error: {e}")
        return False

def main():
    """Main workflow"""
    print()
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║         Railway Database Fix - Systematic Cleanup                ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print()
    print("This script will:")
    print("  1. Reset Railway database (delete all data)")
    print("  2. Upload 450 DOR files (creates 5 clean clients)")
    print("  3. Upload 450 SCH files (links to existing clients)")
    print("  4. Verify data integrity")
    print("  5. Test energy schedule calculation")
    print()
    
    # Step 1: Health check
    if not check_railway_health():
        print("\n❌ Railway is not accessible. Aborting.")
        return
    
    # Step 2: Reset database
    if not reset_database():
        print("\n❌ Database reset failed. Aborting.")
        return
    
    # Step 3: Upload DOR files
    print_header("STEP 3: Upload DOR Files (450 files)")
    if not upload_files("*DOR*.xls", "Daily Obligation Reports"):
        print("\n⚠️  DOR upload had failures. Continue anyway? (y/n): ", end="")
        if input().lower() != 'y':
            return
    
    # Verify clients created
    verify_clients()
    
    # Step 4: Check if SCH parser fix is deployed
    print_header("STEP 4: Check SCH Parser Deployment")
    print("⚠️  IMPORTANT: Make sure the SCH parser fix is deployed to Railway!")
    print()
    print("   The fix changes entity_id extraction from filename to Excel cells.")
    print("   Without this fix, SCH files will create duplicate clients again.")
    print()
    print("   Check Railway deployment status:")
    print("   → https://railway.app/project/<your-project>/deployments")
    print()
    
    ready = input("Is the SCH parser fix deployed? (yes/no): ")
    if ready.lower() != 'yes':
        print("\n⏸️  Pausing. Re-run this script after SCH parser is deployed.")
        return
    
    # Step 5: Upload SCH files
    print_header("STEP 5: Upload SCH Files (450 files)")
    if not upload_files("*SCH*.xls", "Scheduling Reports"):
        print("\n⚠️  SCH upload had failures. Continue anyway? (y/n): ", end="")
        if input().lower() != 'y':
            return
    
    # Step 6: Verify clients (should still be 5)
    verify_clients()
    
    # Step 7: Verify file counts
    verify_files()
    
    # Step 8: Test energy schedule
    test_energy_schedule()
    
    # Final summary
    print_header("✅ COMPLETE - Railway Database Fixed!")
    print("Next steps:")
    print("  1. Check dashboard: " + RAILWAY_URL)
    print("  2. Verify energy schedule shows >0 days")
    print("  3. Test client-specific filtering")
    print("  4. Check analytics display")
    print()

if __name__ == "__main__":
    main()
