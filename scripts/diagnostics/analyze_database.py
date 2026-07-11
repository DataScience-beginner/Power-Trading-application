#!/usr/bin/env python3
"""
Detailed Railway Database Analysis
Shows why mock data might not be transferring correctly
"""

from database.config import SessionLocal
from database.models import Client, Portfolio, DailyFile, Transaction, EnergyScheduleDay
from sqlalchemy import func
from datetime import datetime, timedelta

db = SessionLocal()

print("\n" + "="*80)
print("DETAILED RAILWAY DATABASE ANALYSIS")
print("="*80 + "\n")

# 1. Count records
print("📊 RECORD COUNTS:")
print(f"   Clients: {db.query(Client).count()}")
print(f"   Portfolios: {db.query(Portfolio).count()}")
print(f"   DailyFiles: {db.query(DailyFile).count()}")
print(f"   Transactions: {db.query(Transaction).count()}")
print(f"   Energy Schedule Days: {db.query(EnergyScheduleDay).count()}")

# 2. Files by type
print(f"\n📄 DAILY FILES BREAKDOWN:")
dor_gdam = db.query(DailyFile).filter(DailyFile.report_type == "DOR-GDAM").count()
dor_dam = db.query(DailyFile).filter(DailyFile.report_type == "DOR-DAM").count()
dor_rtm = db.query(DailyFile).filter(DailyFile.report_type == "DOR-RTM").count()
sch_gdam = db.query(DailyFile).filter(DailyFile.report_type == "SCH-GDAM").count()
sch_dam = db.query(DailyFile).filter(DailyFile.report_type == "SCH-DAM").count()
sch_rtm = db.query(DailyFile).filter(DailyFile.report_type == "SCH-RTM").count()

print(f"   DOR Reports: {dor_gdam + dor_dam + dor_rtm} total")
print(f"      - GDAM: {dor_gdam}")
print(f"      - DAM: {dor_dam}")
print(f"      - RTM: {dor_rtm}")
print(f"   SCH Reports: {sch_gdam + sch_dam + sch_rtm} total")
print(f"      - GDAM: {sch_gdam}")
print(f"      - DAM: {sch_dam}")
print(f"      - RTM: {sch_rtm}")

# 3. Date range
print(f"\n📅 DATE COVERAGE:")
dates = db.query(DailyFile.trading_date).distinct().order_by(DailyFile.trading_date).all()
if dates:
    dates_list = [d[0] for d in dates]
    print(f"   Earliest: {min(dates_list)}")
    print(f"   Latest: {max(dates_list)}")
    print(f"   Unique dates: {len(dates_list)}")
    print(f"   Dates: {', '.join(str(d) for d in sorted(dates_list))}")

# 4. Portfolio coverage
print(f"\n📁 PORTFOLIO FILE COVERAGE:")
portfolios = db.query(Portfolio).all()
for portfolio in portfolios[:5]:  # First 5 portfolios
    file_count = db.query(DailyFile).filter(DailyFile.portfolio_id == portfolio.id).count()
    if file_count > 0:
        print(f"   {portfolio.portfolio_code}: {file_count} files")
        
# 5. Check for missing data patterns
print(f"\n🔍 DATA COMPLETENESS CHECK:")
# For each unique date, check what report types exist
for date in sorted(dates_list)[:3]:  # First 3 dates
    print(f"\n   Date: {date}")
    files_on_date = db.query(DailyFile).filter(DailyFile.trading_date == date).all()
    report_types = {}
    for f in files_on_date:
        report_types[f.report_type] = report_types.get(f.report_type, 0) + 1
    for rtype, count in sorted(report_types.items()):
        print(f"      {rtype}: {count} files")

# 6. Check Energy Schedule status
print(f"\n⚡ ENERGY SCHEDULE STATUS:")
es_days = db.query(EnergyScheduleDay).all()
if es_days:
    print(f"   Total days with schedule data: {len(es_days)}")
    # Group by date
    es_dates = {}
    for day in es_days:
        date_str = str(day.trading_date)
        es_dates[date_str] = {
            'has_gdam': day.has_gdam_data,
            'has_dam': day.has_dam_data,
            'has_rtm': day.has_rtm_data,
            'has_sch': day.has_sch_data
        }
    
    print(f"\n   Sample Energy Schedule Days:")
    for date_str, status in list(es_dates.items())[:5]:
        flags = []
        if status['has_gdam']: flags.append('GDAM✓')
        if status['has_dam']: flags.append('DAM✓')
        if status['has_rtm']: flags.append('RTM✓')
        if status['has_sch']: flags.append('SCH✓')
        print(f"      {date_str}: {', '.join(flags) if flags else 'No data flags'}")
else:
    print(f"   ❌ No Energy Schedule Days found")

# 7. Identify potential issues
print(f"\n⚠️  POTENTIAL ISSUES:")
issues_found = False

# Check if we have matching DOR + SCH pairs for calculation
print(f"\n   Checking DOR + SCH pairing for calculations:")
for date in sorted(dates_list)[:3]:
    # For calculation we need: DOR from previous day + SCH from current day
    prev_date = date - timedelta(days=1)
    
    dor_count = db.query(DailyFile).filter(
        DailyFile.trading_date == prev_date,
        DailyFile.main_category == "DOR"
    ).count()
    
    sch_count = db.query(DailyFile).filter(
        DailyFile.trading_date == date,
        DailyFile.main_category == "SCH"
    ).count()
    
    status = "✓ Can calculate" if (dor_count > 0 and sch_count > 0) else "❌ Missing files"
    print(f"      {date}: DOR({prev_date})={dor_count}, SCH({date})={sch_count} → {status}")

db.close()

print("\n" + "="*80)
print("✅ Analysis complete!")
print("="*80 + "\n")
