#!/usr/bin/env python3
"""
Direct database inspection for Railway PostgreSQL
Check what's actually stored in the database tables
"""

import requests
import json

RAILWAY_URL = "https://power-trading-application-production.up.railway.app"

print("\n" + "="*70)
print("RAILWAY DATABASE INSPECTION")
print("="*70 + "\n")

# 1. Clients
print("1. CLIENTS TABLE:")
print("-"*70)
r = requests.get(f"{RAILWAY_URL}/api/clients")
data = r.json()
clients = data.get('clients', [])
print(f"Total: {len(clients)}\n")

if clients:
    for c in clients:
        client_id = c['id']
        print(f"Client ID: {client_id}")
        print(f"  Name: {c['entity_name']}")
        print(f"  Entity ID: {c['entity_id']}")
        print(f"  Portfolios: {c.get('portfolio_count', 0)}\n")
else:
    print("❌ No clients found!\n")
    exit()

# 2. Check if we can get transactions for this client
print("\n2. CHECKING TRANSACTIONS:")
print("-"*70)

client_id = clients[0]['id']

# Try different endpoints to find transactions
endpoints_to_try = [
    f"/api/clients/{client_id}/files",
    f"/api/clients/{client_id}/transactions",
    f"/api/transactions?client_id={client_id}",
    f"/api/transactions?limit=10",
    f"/api/analytics/client/{client_id}",
]

for endpoint in endpoints_to_try:
    try:
        r = requests.get(f"{RAILWAY_URL}{endpoint}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ {endpoint}")
            print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
            if isinstance(data, dict) and 'files' in data:
                print(f"   Files found: {len(data['files'])}")
            elif isinstance(data, dict) and 'transactions' in data:
                print(f"   Transactions found: {len(data['transactions'])}")
            elif isinstance(data, list):
                print(f"   Items: {len(data)}")
        else:
            print(f"❌ {endpoint} → {r.status_code}")
    except Exception as e:
        print(f"❌ {endpoint} → Error: {e}")

# 3. Check database stats
print("\n3. DATABASE STATISTICS:")
print("-"*70)

try:
    r = requests.get(f"{RAILWAY_URL}/api/analytics/summary", timeout=10)
    if r.status_code == 200:
        stats = r.json()
        print(f"Analytics response: {json.dumps(stats, indent=2)}")
    else:
        print(f"❌ Analytics endpoint failed: {r.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("INSPECTION COMPLETE")
print("="*70 + "\n")
