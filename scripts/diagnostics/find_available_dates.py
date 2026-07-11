#!/usr/bin/env python3
"""
Direct SQL query to see what dates are in Railway PostgreSQL DailyFile table
"""

import requests

RAILWAY_URL = "https://power-trading-application-production.up.railway.app"

print("\n" + "="*70)
print("CHECKING DAILY FILES IN DATABASE")
print("="*70 + "\n")

# First, let's add an endpoint to the API to query daily files
# For now, let's test by triggering calculation for different dates

test_dates = [
    "2026-01-02",  # Needs DOR Jan 1, SCH Jan 2
    "2026-01-03",  # Needs DOR Jan 2, SCH Jan 3
    "2026-01-10",  # Needs DOR Jan 9, SCH Jan 10
    "2026-01-15",  # Needs DOR Jan 14, SCH Jan 15
    "2026-01-20",  # Needs DOR Jan 19, SCH Jan 20
]

# Get client ID
r = requests.get(f"{RAILWAY_URL}/api/clients")
clients = r.json().get('clients', [])

if not clients:
    print("❌ No clients found!")
    exit()

client_id = clients[0]['id']
print(f"Testing with client ID: {client_id}")
print(f"Client: {clients[0]['entity_name']}\n")

print("Testing different calculation dates to find which dates have files:\n")
print(f"{'Calc Date':<15} {'DOR Date':<15} {'SCH Date':<15} {'Status':<20} {'Files Found'}")
print("-" * 90)

for calc_date in test_dates:
    try:
        payload = {"client_id": client_id, "calculation_date": calc_date}
        r = requests.post(
            f"{RAILWAY_URL}/api/calculate/energy-schedule",
            json=payload,
            timeout=10
        )
        
        if r.status_code == 200:
            result = r.json()
            validation = result.get('validation', {})
            status = validation.get('status', 'unknown')
            files_found = validation.get('files_found', {}).get('count_summary', '?')
            dor_date = validation.get('dor_date', '?')
            sch_date = validation.get('sch_date', '?')
            
            print(f"{calc_date:<15} {dor_date:<15} {sch_date:<15} {status:<20} {files_found}")
        else:
            print(f"{calc_date:<15} {'?':<15} {'?':<15} {'ERROR':<20} {r.status_code}")
    except Exception as e:
        print(f"{calc_date:<15} {'?':<15} {'?':<15} {'ERROR':<20} {str(e)[:20]}")

print("\n" + "="*70)
print("\nIf all show '0+0', files aren't being saved to database properly.")
print("If some show files, those dates have data!\n")
