"""
Test the complete energy schedule calculation workflow
Tests with mock data for Jan 13-22, 2026
"""

import requests
from datetime import datetime, timedelta
import json

BASE_URL = "http://localhost:8000"
START_DATE = datetime(2026, 1, 14)  # First calculation date (needs DOR from Jan 13)
NUM_TESTS = 10

def test_calculation_for_date(test_date):
    """Test calculation for a specific date"""
    date_str = test_date.strftime("%Y-%m-%d")
    
    print(f"\n{'='*80}")
    print(f"Testing: {date_str}")
    print(f"{'='*80}")
    
    try:
        # Call the calculate endpoint
        response = requests.post(
            f"{BASE_URL}/api/calculate/energy-schedule",
            params={"calculation_date": date_str},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print(f"✅ SUCCESS!")
                print(f"   Energy Savings: {result['results']['energy_savings_kwh']:.2f} kWh")
                print(f"   Cost Savings: ₹{result['results']['cost_savings_inr']:.2f}")
                print(f"   Total Consumption: {result['results']['total_consumption_kwh']:.2f} kWh")
                print(f"   Total Cost: ₹{result['results']['total_cost_inr']:.2f}")
                print(f"   Excel File: {result['excel_path']}")
                print(f"   Database ID: {result['daily_id']}")
                return True
            else:
                print(f"⚠️  Validation issue: {result.get('message')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def verify_database():
    """Verify calculations were stored in database"""
    print(f"\n{'='*80}")
    print(f"DATABASE VERIFICATION")
    print(f"{'='*80}\n")
    
    try:
        response = requests.get(f"{BASE_URL}/api/energy-schedule/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data.get('calculations', []))} calculations in database")
            
            for calc in data.get('calculations', [])[:5]:  # Show first 5
                print(f"   - {calc['calculation_date']}: {calc['energy_savings_kwh']:.2f} kWh saved")
            
            return True
        else:
            print(f"❌ Failed to fetch status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    """Run complete test suite"""
    print("=" * 80)
    print("ENERGY SCHEDULE CALCULATION - COMPLETE WORKFLOW TEST")
    print("=" * 80)
    print(f"Testing dates: {START_DATE.strftime('%Y-%m-%d')} to {(START_DATE + timedelta(days=NUM_TESTS-1)).strftime('%Y-%m-%d')}")
    print(f"Total tests: {NUM_TESTS}")
    print("=" * 80)
    
    # Test backend health
    print("\n🔍 Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {str(e)}")
        print("Please ensure the FastAPI server is running on port 8000")
        return
    
    # Run calculations for each test date
    success_count = 0
    failed_count = 0
    
    for day in range(NUM_TESTS):
        test_date = START_DATE + timedelta(days=day)
        
        if test_calculation_for_date(test_date):
            success_count += 1
        else:
            failed_count += 1
    
    # Summary
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successful: {success_count}/{NUM_TESTS}")
    print(f"❌ Failed: {failed_count}/{NUM_TESTS}")
    print(f"{'='*80}")
    
    # Verify database
    verify_database()
    
    print(f"\n{'='*80}")
    print(f"NEXT STEPS")
    print(f"{'='*80}")
    print("1. Check calculations/2026/JAN_2026.xlsx to see populated data")
    print("2. Open SQLite database to verify energy_schedule_daily table")
    print("3. View results in the React dashboard")
    print("4. Test date selection in the Calculate dialog")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
