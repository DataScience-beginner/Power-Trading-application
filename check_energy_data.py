"""Quick check of energy schedule data"""
from database.config import SessionLocal
from database.models import EnergyScheduleDay, EnergyScheduleMonth

db = SessionLocal()

# Check days
days = db.query(EnergyScheduleDay).all()
print(f"\n✅ Energy Schedule Days: {len(days)}")
for d in days[:3]:
    print(f"   {d.trading_date}: Scheduled={d.total_scheduled_mwh:.2f} MWh, Consumption={d.total_consumption_after_losses_mwh:.2f} MWh, CTU Loss={d.ctu_losses_percent:.2f}%")

# Check months
months = db.query(EnergyScheduleMonth).all()
print(f"\n✅ Energy Schedule Months: {len(months)}")
for m in months:
    print(f"   {m.month_name}: Total={m.total_scheduled_mwh:.2f} MWh, Days={m.days_completed}")

db.close()
