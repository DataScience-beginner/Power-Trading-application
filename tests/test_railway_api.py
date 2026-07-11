"""Test Railway API endpoints"""
import requests
import json
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://power-trading-application-production.up.railway.app"

print("Testing Railway API Endpoints")
print("=" * 80)

# Test 1: Analytics Summary
print("\n1. Testing /api/analytics/summary")
try:
    response = requests.get(f"{BASE_URL}/api/analytics/summary", timeout=10, verify=False)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   DOR Files: {data.get('dor_count', 'N/A')}")
        print(f"   SCH Files: {data.get('sch_count', 'N/A')}")
        print(f"   Total Transactions: {data.get('total_transactions', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Transactions
print("\n2. Testing /api/transactions/all")
try:
    response = requests.get(f"{BASE_URL}/api/transactions/all", timeout=10, verify=False)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success', False)}")
        print(f"   Total Count: {data.get('total_count', 'N/A')}")
        print(f"   Returned Count: {data.get('count', 'N/A')}")
        if 'transactions' in data:
            print(f"   Transactions is array: {isinstance(data['transactions'], list)}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Energy Schedule Status
print("\n3. Testing /api/energy-schedule/status")
try:
    response = requests.get(f"{BASE_URL}/api/energy-schedule/status", timeout=10, verify=False)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Files endpoint
print("\n4. Testing /api/files")
try:
    response = requests.get(f"{BASE_URL}/api/files?page=1&page_size=10", timeout=10, verify=False)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Total Files: {data.get('total', 'N/A')}")
        print(f"   Files returned: {len(data.get('files', []))}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 80)
