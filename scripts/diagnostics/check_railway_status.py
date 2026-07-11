#!/usr/bin/env python3
"""
Check Railway database status - clients, portfolios, files
"""

import requests
import json

RAILWAY_URL = "https://power-trading-application-production.up.railway.app"

def check_status():
    print("\n" + "="*70)
    print("RAILWAY DATABASE STATUS CHECK")
    print("="*70 + "\n")
    
    # 1. Check clients
    print("1. CLIENTS:")
    print("-" * 70)
    try:
        r = requests.get(f"{RAILWAY_URL}/api/clients", timeout=10)
        if r.status_code == 200:
            data = r.json()
            clients = data.get('clients', [])
            print(f"   Total clients: {len(clients)}\n")
            for c in clients:
                print(f"   ID: {c['id']}")
                print(f"   Name: {c['entity_name']}")
                print(f"   Entity ID: {c['entity_id']}")
                print(f"   Portfolios: {c.get('portfolio_count', 0)}")
                print()
        else:
            print(f"   ❌ Error: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Check portfolios
    print("\n2. PORTFOLIOS:")
    print("-" * 70)
    try:
        r = requests.get(f"{RAILWAY_URL}/api/portfolios", timeout=10)
        if r.status_code == 200:
            portfolios = r.json()
            print(f"   Total portfolios: {len(portfolios)}\n")
            for p in portfolios[:10]:  # Show first 10
                print(f"   {p.get('portfolio_code')} - {p.get('portfolio_name', 'N/A')}")
        else:
            print(f"   ❌ Error: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Check daily files in database (not output folder)
    print("\n3. DAILY FILES (Database Records):")
    print("-" * 70)
    try:
        r = requests.get(f"{RAILWAY_URL}/api/daily-files", timeout=10)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                files = data.get('files', [])
                print(f"   Total daily files: {len(files)}")
                
                dor_files = [f for f in files if 'DOR' in f.get('report_type', '')]
                sch_files = [f for f in files if 'SCH' in f.get('report_type', '')]
                
                print(f"   DOR files: {len(dor_files)}")
                print(f"   SCH files: {len(sch_files)}\n")
                
                if files:
                    print("   Sample files:")
                    for f in files[:5]:
                        print(f"   - {f.get('filename', 'N/A')} (Date: {f.get('trading_date', 'N/A')}, Type: {f.get('report_type', 'N/A')})")
            else:
                print(f"   Total files: {len(data) if isinstance(data, list) else 0}")
        else:
            print(f"   ❌ Error: {r.status_code} - Endpoint may not exist")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Test calculation with a specific date we know we have
    print("\n4. TESTING ENERGY SCHEDULE CALCULATION:")
    print("-" * 70)
    print("   Looking for a date where we have both DOR and SCH files...\n")
    
    # We uploaded DOR for Jan 1-30 and SCH for Jan 2-31
    # So we should have pairs for Jan 2-30
    # Let's try Jan 2, 2026 (needs DOR from Jan 1, SCH from Jan 2)
    
    try:
        r = requests.get(f"{RAILWAY_URL}/api/clients", timeout=10)
        if r.status_code == 200:
            clients = r.json().get('clients', [])
            if clients:
                client_id = clients[0]['id']
                print(f"   Using client ID: {client_id}")
                print(f"   Testing calculation for: 2026-01-02")
                print(f"   Required files: DOR from 2026-01-01, SCH from 2026-01-02\n")
                
                payload = {"client_id": client_id, "calculation_date": "2026-01-02"}
                r = requests.post(f"{RAILWAY_URL}/api/calculate/energy-schedule", json=payload, timeout=30)
                
                print(f"   Status: {r.status_code}")
                result = r.json()
                print(f"   Success: {result.get('success', False)}")
                print(f"   Message: {result.get('message', 'N/A')}")
                
                if 'validation' in result:
                    v = result['validation']
                    print(f"\n   Validation Details:")
                    print(f"   - Status: {v.get('status')}")
                    print(f"   - Files Found: {v.get('files_found', {}).get('count_summary', 'N/A')}")
                    print(f"   - DOR Markets: {v.get('files_found', {}).get('dor_markets', [])}")
                    print(f"   - SCH Markets: {v.get('files_found', {}).get('sch_markets', [])}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("END OF STATUS CHECK")
    print("="*70 + "\n")

if __name__ == "__main__":
    check_status()
