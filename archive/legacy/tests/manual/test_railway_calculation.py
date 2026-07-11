#!/usr/bin/env python3
"""
Test energy schedule calculation with current data
"""

import requests
import json

RAILWAY_URL = "https://power-trading-application-production.up.railway.app"

def test_calculation():
    """Test energy schedule calculation"""
    
    # Get clients
    print("Fetching clients...")
    response = requests.get(f"{RAILWAY_URL}/api/clients")
    if response.status_code != 200:
        print(f"❌ Failed to fetch clients: {response.status_code}")
        return
    
    data = response.json()
    clients = data.get('clients', [])
    
    if not clients:
        print("❌ No clients found!")
        return
    
    client = clients[0]
    print(f"✅ Using client: {client['entity_name']} (ID: {client['id']})")
    
    # Try to calculate for Jan 2, 2026
    # This requires DOR from Jan 1 and SCH from Jan 2
    print("\n Attempting energy schedule calculation for Jan 2, 2026...")
    print("   (Note: This requires both DOR and SCH files, we only have DOR)")
    
    payload = {
        "client_id": client['id'],
        "calculation_date": "2026-01-02"
    }
    
    response = requests.post(
        f"{RAILWAY_URL}/api/calculate/energy-schedule",
        json=payload,
        timeout=30
    )
    
    print(f"\nResponse status: {response.status_code}")
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

if __name__ == "__main__":
    test_calculation()
