"""Populate energy schedule data directly into database for dashboard display"""
import sys
import os
from datetime import date, timedelta
from decimal import Decimal
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.config import SessionLocal
from database.models import EnergyScheduleDay, EnergyScheduleMonth, DailyFile, Portfolio
from sqlalchemy import func

def populate_energy_schedules():
    """Create energy schedule records for Jan 11-16, 2026"""
    db = SessionLocal()
    
    try:
        portfolio_code = "NPT0019_TN0"
        
        # First, create monthly record for January 2026
        print("=" * 80)
        print("POPULATING ENERGY SCHEDULE DATA")
        print("=" * 80)
        
        # Get portfolio ID
        portfolio = db.query(Portfolio).filter(Portfolio.portfolio_code == portfolio_code).first()
        if not portfolio:
            print(f"❌ Portfolio {portfolio_code} not found")
            return
        
        print(f"📁 Portfolio: {portfolio.portfolio_code} (ID: {portfolio.id})")
        
        # Check if month record exists
        month_record = db.query(EnergyScheduleMonth).filter(
            EnergyScheduleMonth.portfolio_id == portfolio.id,
            EnergyScheduleMonth.month == 1,
            EnergyScheduleMonth.year == 2026
        ).first()
        
        if not month_record:
            month_record = EnergyScheduleMonth(
                portfolio_id=portfolio.id,
                month=1,
                year=2026,
                month_name="January 2026",
                total_scheduled_mwh=0.0,
                total_consumption_after_losses_mwh=0.0,
                total_energy_savings_mwh=0.0,
                total_gdam_cost=0.0,
                total_dam_cost=0.0,
                total_rtm_cost=0.0,
                average_ctu_losses_percent=0.0,
                days_completed=0,
                is_complete=0
            )
            db.add(month_record)
            db.flush()
            print(f"\n✅ Created monthly record: January 2026")
        else:
            print(f"\n♻️  Monthly record already exists: January 2026")
        
        # Create daily records for Jan 11-16
        start_date = date(2026, 1, 11)
        end_date = date(2026, 1, 16)
        
        current_date = start_date
        created_count = 0
        updated_count = 0
        
        while current_date <= end_date:
            # Check if daily record exists
            existing = db.query(EnergyScheduleDay).filter(
                EnergyScheduleDay.trading_date == current_date,
                EnergyScheduleDay.month_sheet_id == month_record.id
            ).first()
            
            # Get DOR data from previous day for charges
            dor_date = current_date - timedelta(days=1)
            
            # Get GDAM data
            gdam_file = db.query(DailyFile).filter(
                DailyFile.trading_date == dor_date,
                DailyFile.portfolio_id == portfolio.id,
                DailyFile.report_type == 'DOR-GDAM'
            ).first()
            
            if gdam_file and gdam_file.summary:
                gdam_summary = json.loads(gdam_file.summary) if isinstance(gdam_file.summary, str) else gdam_file.summary
            else:
                gdam_summary = {}
            gdam_qty = float(gdam_summary.get('total_buy_mwh', 0.0))
            gdam_cost = abs(float(gdam_summary.get('total_buy_mwh', 0.0))) * 4.0  # Mock cost calculation
            
            # Get DAM data
            dam_file = db.query(DailyFile).filter(
                DailyFile.trading_date == dor_date,
                DailyFile.portfolio_id == portfolio.id,
                DailyFile.report_type == 'DOR-DAM'
            ).first()
            
            if dam_file and dam_file.summary:
                dam_summary = json.loads(dam_file.summary) if isinstance(dam_file.summary, str) else dam_file.summary
            else:
                dam_summary = {}
            dam_qty = float(dam_summary.get('total_buy_mwh', 0.0))
            dam_cost = abs(float(dam_summary.get('total_buy_mwh', 0.0))) * 4.0
            
            # Get RTM data
            rtm_file = db.query(DailyFile).filter(
                DailyFile.trading_date == dor_date,
                DailyFile.portfolio_id == portfolio.id,
                DailyFile.report_type == 'DOR-RTM'
            ).first()
            
            if rtm_file and rtm_file.summary:
                rtm_summary = json.loads(rtm_file.summary) if isinstance(rtm_file.summary, str) else rtm_file.summary
            else:
                rtm_summary = {}
            rtm_qty = float(rtm_summary.get('total_buy_mwh', 0.0))
            rtm_cost = abs(float(rtm_summary.get('total_buy_mwh', 0.0))) * 4.0
            
            # Get SCH data for consumption after losses
            sch_file = db.query(DailyFile).filter(
                DailyFile.trading_date == current_date,
                DailyFile.portfolio_id == portfolio.id,
                DailyFile.report_type.like('SCH%')
            ).first()
            
            if sch_file and sch_file.summary:
                sch_summary = json.loads(sch_file.summary) if isinstance(sch_file.summary, str) else sch_file.summary
            else:
                sch_summary = {}
            # SCH files have total_scheduled_mwh (which is the interface/after-loss value)
            consumption_after_losses = abs(float(sch_summary.get('total_scheduled_mwh', 0.0)))
            
            # Calculate totals
            total_scheduled = gdam_qty + dam_qty + rtm_qty
            total_cost = gdam_cost + dam_cost + rtm_cost
            ctu_losses = total_scheduled - consumption_after_losses if total_scheduled > 0 else 0.0
            ctu_losses_pct = (ctu_losses / total_scheduled * 100) if total_scheduled > 0 else 0.0
            
            if existing:
                # Update existing record
                existing.gdam_scheduled_quantity_mwh = gdam_qty
                existing.gdam_cost = gdam_cost
                existing.dam_scheduled_quantity_mwh = dam_qty
                existing.dam_cost = dam_cost
                existing.rtm_scheduled_quantity_mwh = rtm_qty
                existing.rtm_cost = rtm_cost
                existing.total_consumption_after_losses_mwh = consumption_after_losses
                existing.total_scheduled_mwh = total_scheduled
                existing.total_cost = total_cost
                existing.ctu_losses_mwh = ctu_losses
                existing.ctu_losses_percent = ctu_losses_pct
                existing.has_gdam_data = 1 if gdam_file else 0
                existing.has_dam_data = 1 if dam_file else 0
                existing.has_rtm_data = 1 if rtm_file else 0
                existing.has_sch_data = 1 if sch_file else 0
                updated_count += 1
                print(f"   ♻️  Updated {current_date}: SCH={total_scheduled:.2f} MW, Consumption={consumption_after_losses:.2f} MW, Cost=₹{total_cost:.2f}")
            else:
                # Create new record
                day_record = EnergyScheduleDay(
                    month_sheet_id=month_record.id,
                    trading_date=current_date,
                    day_of_month=current_date.day,
                    gdam_scheduled_quantity_mwh=gdam_qty,
                    gdam_cost=gdam_cost,
                    dam_scheduled_quantity_mwh=dam_qty,
                    dam_cost=dam_cost,
                    rtm_scheduled_quantity_mwh=rtm_qty,
                    rtm_cost=rtm_cost,
                    total_consumption_after_losses_mwh=consumption_after_losses,
                    total_scheduled_mwh=total_scheduled,
                    total_cost=total_cost,
                    ctu_losses_mwh=ctu_losses,
                    ctu_losses_percent=ctu_losses_pct,
                    has_gdam_data=1 if gdam_file else 0,
                    has_dam_data=1 if dam_file else 0,
                    has_rtm_data=1 if rtm_file else 0,
                    has_sch_data=1 if sch_file else 0,
                    is_complete=1 if (gdam_file and dam_file and rtm_file and sch_file) else 0
                )
                db.add(day_record)
                created_count += 1
                print(f"   ✅ Created {current_date}: SCH={total_scheduled:.2f} MW, Consumption={consumption_after_losses:.2f} MW, Cost=₹{total_cost:.2f}")
            
            current_date += timedelta(days=1)
        
        # Commit the daily records first
        db.commit()
        
        # Now update monthly totals after commit
        monthly_totals = db.query(
            func.sum(EnergyScheduleDay.total_scheduled_mwh).label('total_sch'),
            func.sum(EnergyScheduleDay.total_consumption_after_losses_mwh).label('total_consumption'),
            func.sum(EnergyScheduleDay.gdam_cost).label('total_gdam'),
            func.sum(EnergyScheduleDay.dam_cost).label('total_dam'),
            func.sum(EnergyScheduleDay.rtm_cost).label('total_rtm'),
            func.sum(EnergyScheduleDay.total_cost).label('total_cost'),
            func.avg(EnergyScheduleDay.ctu_losses_percent).label('avg_ctu_losses')
        ).filter(
            EnergyScheduleDay.month_sheet_id == month_record.id
        ).first()
        
        if monthly_totals:
            month_record.total_scheduled_mwh = float(monthly_totals.total_sch or 0.0)
            month_record.total_consumption_after_losses_mwh = float(monthly_totals.total_consumption or 0.0)
            month_record.total_gdam_cost = float(monthly_totals.total_gdam or 0.0)
            month_record.total_dam_cost = float(monthly_totals.total_dam or 0.0)
            month_record.total_rtm_cost = float(monthly_totals.total_rtm or 0.0)
            month_record.average_ctu_losses_percent = float(monthly_totals.avg_ctu_losses or 0.0)
            month_record.days_completed = created_count + updated_count
        
        # Commit monthly updates
        db.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Created: {created_count} days")
        print(f"♻️  Updated: {updated_count} days")
        print(f"\n📊 MONTHLY SUMMARY (January 2026):")
        print(f"   Total Scheduled: {month_record.total_scheduled_mwh:.2f} MWh")
        print(f"   Total Consumption After Losses: {month_record.total_consumption_after_losses_mwh:.2f} MWh")
        print(f"   Total GDAM Cost: ₹{month_record.total_gdam_cost:.2f}")
        print(f"   Total DAM Cost: ₹{month_record.total_dam_cost:.2f}")
        print(f"   Total RTM Cost: ₹{month_record.total_rtm_cost:.2f}")
        print(f"   Average CTU Losses: {month_record.average_ctu_losses_percent:.2f}%")
        print(f"   Days Completed: {month_record.days_completed}")
        print("=" * 80)
        
        # Verify counts
        total_days = db.query(EnergyScheduleDay).count()
        total_months = db.query(EnergyScheduleMonth).count()
        print(f"\n📈 Database now has:")
        print(f"   Energy Schedule Days: {total_days}")
        print(f"   Energy Schedule Months: {total_months}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    populate_energy_schedules()
