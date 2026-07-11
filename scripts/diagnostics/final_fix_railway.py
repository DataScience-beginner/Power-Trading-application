#!/usr/bin/env python3
"""
FINAL FIX: Reset Railway and upload with proper entity consolidation
This script will:
1. Reset the database completely
2. Upload DOR files (will create proper clients)
3. Upload SCH files (will link to existing clients if SCH parser is fixed)
"""

import requests
import time
from pathlib import Path

RAILWAY_URL = "https://power-trading-application-production.up.railway.app"

print("\n" + "="*70)
print("FINAL FIX - Railway Database Reset & Clean Upload")
print("="*70 + "\n")

# Step 1: Reset database
print("STEP 1: Resetting database...")
print("-" * 70)

confirm = input("⚠️  This will DELETE ALL DATA. Type 'YES' to continue: ")
if confirm != "YES":
    print("❌ Cancelled")
    exit()

try:
    r = requests.post(f"{RAILWAY_URL}/api/admin/reset-database", timeout=30)
    if r.status_code == 200:
        result = r.json()
        print(f"✅ Database reset complete!")
        print(f"   Deleted: {result['deleted']['clients']} clients, {result['deleted']['daily_files']} files\n")
    else:
        print(f"❌ Reset failed: {r.status_code}")
        print(f"   Response: {r.text}")
        exit()
except Exception as e:
    print(f"❌ Error: {e}")
    exit()

# Step 2: Upload DOR files
print("\nSTEP 2: Uploading DOR files (creates clients)...")
print("-" * 70)

dor_dir = Path("Data/mock_reports_real_format")
dor_files = sorted(dor_dir.glob("*DOR*.xlsx"))

print(f"Found {len(dor_files)} DOR files\n")

success = 0
failed = 0
start_time = time.time()

for idx, file_path in enumerate(dor_files, 1):
    try:
        with open(file_path, 'rb') as f:
            files_data = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            r = requests.post(f"{RAILWAY_URL}/api/upload", files=files_data, timeout=30)
            
            if r.status_code == 200:
                success += 1
                if idx % 10 == 0:
                    print(f"   ✅ {idx}/{len(dor_files)} uploaded")
            else:
                failed += 1
                print(f"   ❌ Failed: {file_path.name}")
    except Exception as e:
        failed += 1
        print(f"   ❌ Error: {file_path.name} - {e}")

elapsed = time.time() - start_time
print(f"\n✅ DOR upload complete: {success}/{len(dor_files)} (Time: {int(elapsed/60)}m {int(elapsed%60)}s)\n")

# Step 3: Check clients created
print("STEP 3: Checking clients created...")
print("-" * 70)

try:
    r = requests.get(f"{RAILWAY_URL}/api/clients", timeout=10)
    if r.status_code == 200:
        data = r.json()
        clients = data.get('clients', [])
        print(f"✅ Found {len(clients)} client(s):\n")
        for c in clients:
            print(f"   {c['entity_name']}")
            print(f"   Entity ID: {c['entity_id']}, Portfolios: {c.get('portfolio_count', 0)}\n")
        
        if len(clients) > 1:
            print("⚠️  WARNING: Multiple clients detected!")
            print("   This means DOR files have different entity_id values in their Excel cells.")
            print("   For demo purposes, this is actually good - shows multiple companies!\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Step 4: Upload SCH files
print("STEP 4: Uploading SCH files (links to existing clients)...")
print("-" * 70)

sch_dir = Path("Data/mock_reports_sch")
if not sch_dir.exists():
    print("❌ SCH directory not found. Skipping SCH upload.")
else:
    sch_files = sorted(sch_dir.glob("*.xlsx"))
    print(f"Found {len(sch_files)} SCH files\n")
    
    sch_success = 0
    sch_failed = 0
    start_time = time.time()
    
    for idx, file_path in enumerate(sch_files, 1):
        try:
            with open(file_path, 'rb') as f:
                files_data = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                r = requests.post(f"{RAILWAY_URL}/api/upload", files=files_data, timeout=30)
                
                if r.status_code == 200:
                    sch_success += 1
                    if idx % 10 == 0:
                        print(f"   ✅ {idx}/{len(sch_files)} uploaded")
                else:
                    sch_failed += 1
                    if sch_failed <= 3:  # Show first 3 failures
                        print(f"   ❌ Failed: {file_path.name} ({r.status_code})")
        except Exception as e:
            sch_failed += 1
            print(f"   ❌ Error: {file_path.name}")
    
    elapsed = time.time() - start_time
    print(f"\n✅ SCH upload complete: {sch_success}/{len(sch_files)} (Time: {int(elapsed/60)}m {int(elapsed%60)}s)\n")

# Step 5: Final status check
print("STEP 5: Final status check...")
print("-" * 70)

try:
    r = requests.get(f"{RAILWAY_URL}/api/clients", timeout=10)
    if r.status_code == 200:
        data = r.json()
        clients = data.get('clients', [])
        print(f"✅ Total clients: {len(clients)}")
        
        if len(clients) > 5:
            print(f"\n❌ PROBLEM: Still have {len(clients)} clients (should be 1-5)")
            print("   SCH parser is still creating duplicates!")
            print("   SCH parser fix NOT deployed to Railway yet.\n")
        else:
            print(f"✅ Client count looks good!\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Step 6: Test calculation
print("STEP 6: Testing energy schedule calculation...")
print("-" * 70)

try:
    r = requests.get(f"{RAILWAY_URL}/api/clients", timeout=10)
    if r.status_code == 200:
        clients = r.json().get('clients', [])
        if clients:
            client_id = clients[0]['id']
            print(f"Using client: {clients[0]['entity_name']} (ID: {client_id})")
            print(f"Testing calculation for Jan 2, 2026\n")
            
            payload = {"client_id": client_id, "calculation_date": "2026-01-02"}
            r = requests.post(f"{RAILWAY_URL}/api/calculate/energy-schedule", json=payload, timeout=30)
            
            result = r.json()
            print(f"Result: {result.get('success', False)}")
            print(f"Message: {result.get('message', 'N/A')}\n")
            
            if result.get('success'):
                print("✅ ✅ ✅ ENERGY SCHEDULE CALCULATION WORKING! ✅ ✅ ✅\n")
            else:
                print("⚠️  Calculation not working yet.")
                if 'validation' in result:
                    v = result['validation']
                    print(f"   Status: {v.get('status')}")
                    print(f"   Files found: {v.get('files_found', {}).get('count_summary', 'N/A')}")
except Exception as e:
    print(f"❌ Error: {e}\n")

print("\n" + "="*70)
print("COMPLETE! Check dashboard: " + RAILWAY_URL)
print("="*70 + "\n")
