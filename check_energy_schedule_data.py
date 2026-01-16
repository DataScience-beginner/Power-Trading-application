#!/usr/bin/env python3
"""
Test the existing energy schedule workflow that's already built!
Check if the auto-calculation from upload is working.
"""

from database.config import SessionLocal
from database.models import EnergyScheduleDay, Portfolio
from datetime import date

db = SessionLocal()

print("\n" + "="*70)
print("CHECKING EXISTING ENERGY SCHEDULE DATA")
print("="*70 + "\n")

# Check if we have any EnergyScheduleDay records
days = db.query(EnergyScheduleDay).all()

print(f"Total Energy Schedule Days in database: {len(days)}\n")

if days:
    print("Sample records:")
    for day in days[:10]:
        print(f"\nDate: {day.trading_date}")
        print(f"  Complete: {bool(day.is_complete)}")
        print(f"  Files: GDAM={'✅' if day.has_gdam_data else '❌'} DAM={'✅' if day.has_dam_data else '❌'} RTM={'✅' if day.has_rtm_data else '❌'} SCH={'✅' if day.has_sch_data else '❌'}")
        if day.is_complete:
            print(f"  Scheduled: {day.total_scheduled_mwh:.2f} MWh")
            print(f"  CTU Losses: {day.ctu_losses_mwh:.2f} MWh ({day.ctu_losses_percent:.2f}%)")
            print(f"  Energy Saved: {day.energy_savings_mwh:.2f} MWh")
            print(f"  Total Cost: ₹{day.total_cost:,.2f}")
else:
    print("❌ No Energy Schedule Day records found!")
    print("\nThis means the upload endpoint's auto-transfer isn't working.")
    print("OR the files uploaded don't trigger the energy schedule parsers.")

# Check portfolios
portfolios = db.query(Portfolio).all()
print(f"\n\nPortfolios in database: {len(portfolios)}")
for p in portfolios:
    print(f"  - {p.portfolio_code}: {p.portfolio_name}")

db.close()
