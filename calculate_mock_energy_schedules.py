"""Calculate energy schedules for all mock data dates (Jan 11-16, 2026)"""
import sys
import os
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.config import SessionLocal
from database.energy_schedule_service import EnergyScheduleCalculator

def main():
    """Calculate energy schedules for Jan 11-16 (we have DOR data from Jan 10)"""
    db = SessionLocal()
    calculator = EnergyScheduleCalculator()
    
    try:
        # We can calculate from Jan 11 onwards (need DOR from Jan 10)
        start_date = date(2026, 1, 11)
        end_date = date(2026, 1, 16)
        
        current_date = start_date
        success_count = 0
        failed_count = 0
        
        print("=" * 80)
        print("CALCULATING ENERGY SCHEDULES FOR MOCK DATA")
        print("=" * 80)
        
        while current_date <= end_date:
            print(f"\n📅 Processing {current_date.strftime('%Y-%m-%d')}...")
            
            try:
                result = calculator.calculate_energy_schedule(
                    calculation_date=current_date,
                    db=db
                )
                
                if result['status'] == 'success':
                    print(f"   ✅ SUCCESS: {result['message']}")
                    success_count += 1
                else:
                    print(f"   ❌ FAILED: {result['message']}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                failed_count += 1
                
            current_date += timedelta(days=1)
        
        print("\n" + "=" * 80)
        print(f"✅ Successfully calculated: {success_count} days")
        print(f"❌ Failed: {failed_count} days")
        print("=" * 80)
        
        # Show summary of what was created
        if success_count > 0:
            from database.models import EnergyScheduleDay
            total_schedules = db.query(EnergyScheduleDay).count()
            print(f"\n📊 Total Energy Schedule Days in database: {total_schedules}")
            
    finally:
        db.close()

if __name__ == "__main__":
    main()
