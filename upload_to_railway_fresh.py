"""Upload fresh 7-day mock data to Railway database"""
import sys
sys.path.insert(0, '.')

from direct_insert_7day_mock import generate_and_insert_mock_data

def main():
    """Upload 7 days of mock data to Railway"""
    print("=" * 80)
    print("UPLOADING FRESH MOCK DATA TO RAILWAY")
    print("=" * 80)
    print("\nThis will insert:")
    print("  - 1 Client (Grasim Industries Limited)")
    print("  - 1 Portfolio (NPT0019_TN0)")
    print("  - 42 DailyFiles (7 days × 6 report types)")
    print("  - 6,048 Transactions (42 files × 96 timeslots × 1.5 avg)")
    print("\nDate range: Jan 10-16, 2026")
    print("\n" + "=" * 80)
    
    # Run the insertion
    generate_and_insert_mock_data()
    
    print("\n" + "=" * 80)
    print("✅ Fresh mock data uploaded to Railway!")
    print("=" * 80)

if __name__ == "__main__":
    main()
