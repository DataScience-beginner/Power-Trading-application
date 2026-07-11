"""Clean Railway database - delete all data"""
import sys
sys.path.insert(0, '.')

from database.config import SessionLocal
from database.models import (
    Client, Portfolio, DailyFile, Transaction, 
    EnergyScheduleDay, EnergyScheduleMonth, MonthlyCalculation
)

def clean_database():
    """Delete all data from Railway database"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("CLEANING RAILWAY DATABASE")
        print("=" * 80)
        
        # Count before deletion
        print("\nCurrent record counts:")
        print(f"  Clients: {db.query(Client).count()}")
        print(f"  Portfolios: {db.query(Portfolio).count()}")
        print(f"  DailyFiles: {db.query(DailyFile).count()}")
        print(f"  Transactions: {db.query(Transaction).count()}")
        print(f"  Energy Schedule Days: {db.query(EnergyScheduleDay).count()}")
        print(f"  Energy Schedule Months: {db.query(EnergyScheduleMonth).count()}")
        
        print("\n⚠️  WARNING: This will delete ALL data from Railway database!")
        response = input("Type 'YES' to confirm deletion: ")
        
        if response != 'YES':
            print("❌ Deletion cancelled.")
            return
        
        print("\nDeleting data...")
        
        # Delete in correct order (children first)
        db.query(Transaction).delete()
        print("  ✅ Deleted all transactions")
        
        db.query(EnergyScheduleDay).delete()
        print("  ✅ Deleted all energy schedule days")
        
        db.query(EnergyScheduleMonth).delete()
        print("  ✅ Deleted all energy schedule months")
        
        db.query(MonthlyCalculation).delete()
        print("  ✅ Deleted all monthly calculations")
        
        db.query(DailyFile).delete()
        print("  ✅ Deleted all daily files")
        
        db.query(Portfolio).delete()
        print("  ✅ Deleted all portfolios")
        
        db.query(Client).delete()
        print("  ✅ Deleted all clients")
        
        db.commit()
        
        print("\n" + "=" * 80)
        print("✅ Railway database cleaned successfully!")
        print("=" * 80)
        print("\nDatabase is now empty and ready for fresh data.")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error cleaning database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    clean_database()
