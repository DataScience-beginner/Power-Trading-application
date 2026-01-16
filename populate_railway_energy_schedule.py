"""Populate energy schedule data on Railway"""
import sys
sys.path.insert(0, '.')

from populate_energy_schedule_data import populate_energy_schedules

def main():
    """Populate energy schedule data on Railway"""
    print("=" * 80)
    print("POPULATING ENERGY SCHEDULE DATA ON RAILWAY")
    print("=" * 80)
    print("\nThis will create:")
    print("  - 1 Monthly record (January 2026)")
    print("  - 6 Daily records (Jan 11-16, 2026)")
    print("  - Calculated metrics (scheduled MWh, costs, CTU losses)")
    print("\n" + "=" * 80)
    
    # Run the population
    populate_energy_schedules()
    
    print("\n" + "=" * 80)
    print("✅ Energy schedule data populated on Railway!")
    print("=" * 80)

if __name__ == "__main__":
    main()
