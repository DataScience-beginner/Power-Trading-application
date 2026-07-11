"""
Trigger energy schedule calculations for all uploaded data
Processes all days that have complete DOR + SCH file pairs
"""
import requests
from datetime import datetime, timedelta
import time

RAILWAY_URL = "https://power-trading-application-production.up.railway.app"

def trigger_calculation(calculation_date):
    """Trigger energy schedule calculation for a specific date"""
    url = f"{RAILWAY_URL}/api/calculate/energy-schedule"
    
    payload = {
        "portfolio_id": 1,  # Mellbro Sugars portfolio
        "calculation_date": calculation_date.strftime("%Y-%m-%d")
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            return True, result.get('message', 'Success')
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)[:100]

def main():
    """Calculate energy schedules for January 2026"""
    print("="*70)
    print("⚡ ENERGY SCHEDULE CALCULATION - JANUARY 2026")
    print("="*70)
    print(f"Target: {RAILWAY_URL}\n")
    
    # Calculate for Jan 2-30 (need previous day's DOR file)
    start_date = datetime(2026, 1, 2)
    end_date = datetime(2026, 1, 30)
    
    total_days = (end_date - start_date).days + 1
    success_count = 0
    failed_count = 0
    
    print(f"📅 Processing {total_days} days (Jan 2 - Jan 30)\n")
    
    current_date = start_date
    day_num = 1
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        
        print(f"[{day_num:2d}/{total_days}] {date_str}...", end=' ', flush=True)
        
        success, message = trigger_calculation(current_date)
        
        if success:
            print("✅")
            success_count += 1
        else:
            print(f"❌ {message}")
            failed_count += 1
        
        current_date += timedelta(days=1)
        day_num += 1
        time.sleep(0.5)  # Small delay between calculations
    
    print("\n" + "="*70)
    print("📊 CALCULATION RESULTS")
    print("="*70)
    print(f"✅ Success: {success_count}/{total_days}")
    print(f"❌ Failed:  {failed_count}/{total_days}")
    print("="*70)
    
    if success_count > 0:
        print(f"\n🎉 Energy schedules calculated successfully!")
        print(f"📊 View results at: {RAILWAY_URL}/api/energy-schedule/data")
        print(f"📈 Check dashboard: {RAILWAY_URL}\n")

if __name__ == "__main__":
    main()
