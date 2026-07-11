"""Quick deployment verification"""
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://power-trading-application-production.up.railway.app"

print("=" * 80)
print("VERIFYING RAILWAY DEPLOYMENT")
print("=" * 80)

# Test analytics
print("\n✓ Testing analytics summary...")
try:
    r = requests.get(f"{BASE_URL}/api/analytics/summary", timeout=10, verify=False)
    data = r.json()
    
    if 'success' in data and 'summary' in data:
        summary = data['summary']
        dor_files = summary.get('dor_files', 0)
        sch_files = summary.get('sch_files', 0)
        total_txns = summary.get('total_transactions', 0)
        
        print(f"  ✅ DOR Files: {dor_files}")
        print(f"  ✅ SCH Files: {sch_files}")
        print(f"  ✅ Total Transactions: {total_txns}")
        
        if dor_files == 21 and sch_files == 21:
            print("  🎉 PERFECT! Correct data counts!")
        else:
            print(f"  ℹ️  Current: {dor_files} DOR / {sch_files} SCH files")
    else:
        print("  ❌ Analytics response format error")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test energy schedule
print("\n✓ Testing energy schedule...")
try:
    r = requests.get(f"{BASE_URL}/api/energy-schedule/status", timeout=10, verify=False)
    data = r.json()
    
    if data['count'] > 0:
        print(f"  ✅ Energy schedules found: {data['count']}")
        print("  🎉 Energy schedule populated!")
    else:
        print("  ⚠️  No energy schedule data yet")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test transactions limit
print("\n✓ Testing transactions limit...")
try:
    r = requests.get(f"{BASE_URL}/api/transactions/all", timeout=10, verify=False)
    data = r.json()
    
    if data['total_count'] == 6048 and data['count'] <= 10000:
        print(f"  ✅ Total: {data['total_count']}, Returned: {data['count']}")
        print("  🎉 New limit (10,000) is active!")
    elif data['count'] == 1000:
        print(f"  ❌ Old limit (1,000) still active - old code deployed")
    else:
        print(f"  ℹ️  Total: {data.get('total_count', 'unknown')}, Returned: {data.get('count', 'unknown')}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "=" * 80)
print("DEPLOYMENT STATUS:")
print("=" * 80)
print("\n👉 If you see '❌ Old limit' or '❌ Analytics fields missing':")
print("   → Railway is still running OLD code")
print("   → Need to wait for deployment or manually trigger redeploy")
print("\n👉 If you see all '✅' marks:")
print("   → Deployment successful!")
print("   → Open browser and hard refresh (Ctrl+Shift+R)")
print("=" * 80)
