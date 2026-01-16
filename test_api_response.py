"""Test API analytics endpoint response"""
import requests
import json

# Test the analytics summary endpoint
try:
    response = requests.get('http://localhost:8000/api/analytics/summary')
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")

# Test transactions endpoint
try:
    response = requests.get('http://localhost:8000/api/transactions')
    data = response.json()
    print(f"\n\nTransactions endpoint:")
    print(f"Total count returned: {data.get('total_count', 'N/A')}")
    print(f"Transactions in response: {len(data.get('transactions', []))}")
except Exception as e:
    print(f"Error: {e}")

# Test energy schedule status
try:
    response = requests.get('http://localhost:8000/api/energy-schedule/status')
    print(f"\n\nEnergy Schedule Status:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error checking energy schedule: {e}")
