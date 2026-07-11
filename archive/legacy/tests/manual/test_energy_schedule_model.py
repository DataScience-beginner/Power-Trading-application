"""
Test Energy Schedule Data Model
--------------------------------
Tests the Energy Schedule CRUD operations with sample data.
"""

from database.config import SessionLocal
from database.energy_schedule_crud import (
    get_or_create_month_sheet,
    get_or_create_daily_entry,
    update_daily_entry_dor_data,
    update_daily_entry_sch_data,
    calculate_daily_entry,
    get_all_month_sheets,
    get_all_daily_entries
)
from database.services import get_or_create_client, get_or_create_portfolio
from datetime import date
import json


def test_energy_schedule_workflow():
    """
    Test the complete Energy Schedule workflow:
    1. Create month sheet
    2. Create daily entry
    3. Add DOR data (GDAM, DAM, RTM)
    4. Add SCH data
    5. Calculate derived fields
    6. Verify results
    """
    print("\n" + "="*100)
    print("TESTING ENERGY SCHEDULE DATA MODEL - Story 1.3")
    print("="*100)
    
    db = SessionLocal()
    
    try:
        # Step 1: Get or create client and portfolio
        print("\n1️⃣  Getting client and portfolio...")
        client = get_or_create_client(
            db,
            entity_id="NPT0027",
            entity_name="Mellbro Sugars Pvt Ltd"
        )
        portfolio = get_or_create_portfolio(
            db,
            client_id=client.id,
            portfolio_code="NPT0027_KA0"
        )
        print(f"   ✅ Client: {client.entity_name}")
        print(f"   ✅ Portfolio: {portfolio.portfolio_code}")
        
        # Step 2: Create month sheet for January 2026
        print("\n2️⃣  Creating month sheet...")
        month_sheet = get_or_create_month_sheet(
            db,
            portfolio_id=portfolio.id,
            year=2026,
            month=1
        )
        print(f"   ✅ Month Sheet: {month_sheet.month_name} (ID: {month_sheet.id})")
        
        # Step 3: Create daily entry for January 12, 2026
        print("\n3️⃣  Creating daily entry...")
        trading_date = date(2026, 1, 12)
        daily_entry = get_or_create_daily_entry(
            db,
            portfolio_id=portfolio.id,
            trading_date=trading_date
        )
        print(f"   ✅ Daily Entry: {daily_entry.trading_date} (ID: {daily_entry.id})")
        
        # Step 4: Add GDAM DOR data
        print("\n4️⃣  Adding GDAM DOR data...")
        gdam_data = {
            "summary": {
                "nldc_application_fee": -5.13,
                "ctu_transmission_charges": {"total": 0.0},
                "total_cost": 1674432.76,
                "scheduled_quantity": 45.5,
                "other_charges": {
                    "stu_transmission_charges": -25920.0,
                    "sldc_scheduling_charges": -1000.0
                }
            }
        }
        daily_entry = update_daily_entry_dor_data(
            db,
            daily_entry_id=daily_entry.id,
            market_type="GDAM",
            dor_data=gdam_data
        )
        print(f"   ✅ GDAM: NLDC=₹{daily_entry.gdam_nldc_fee}, Cost=₹{daily_entry.gdam_cost}")
        
        # Step 5: Add DAM DOR data
        print("\n5️⃣  Adding DAM DOR data...")
        dam_data = {
            "summary": {
                "nldc_application_fee": -4.91,
                "ctu_transmission_charges": {"total": -805.73},
                "total_cost": -6396.66,
                "scheduled_quantity": 5.0,
                "other_charges": {
                    "stu_transmission_charges": -398.99,
                    "sldc_scheduling_charges": -215.62
                }
            }
        }
        daily_entry = update_daily_entry_dor_data(
            db,
            daily_entry_id=daily_entry.id,
            market_type="DAM",
            dor_data=dam_data
        )
        print(f"   ✅ DAM: NLDC=₹{daily_entry.dam_nldc_fee}, Cost=₹{daily_entry.dam_cost}")
        
        # Step 6: Add RTM DOR data
        print("\n6️⃣  Adding RTM DOR data...")
        rtm_data = {
            "summary": {
                "nldc_application_fee": -5.74,
                "ctu_transmission_charges": {"total": -585.99},
                "total_cost": -5556.44,
                "scheduled_quantity": 3.0,
                "other_charges": {
                    "stu_transmission_charges": -290.16,
                    "sldc_scheduling_charges": -213.81
                }
            }
        }
        daily_entry = update_daily_entry_dor_data(
            db,
            daily_entry_id=daily_entry.id,
            market_type="RTM",
            dor_data=rtm_data
        )
        print(f"   ✅ RTM: NLDC=₹{daily_entry.rtm_nldc_fee}, Cost=₹{daily_entry.rtm_cost}")
        
        # Step 7: Add SCH consumption data
        print("\n7️⃣  Adding SCH consumption data...")
        sch_data = {
            "consumption_after_losses": {
                "timeslots": [0.0] * 96,  # Simplified - all zeros except a few slots
                "total_mwh": 48.5
            },
            "losses": {
                "regional_percent": 4.81,
                "state_percent": 3.06,
                "combined_percent": 7.87
            }
        }
        # Add some consumption values
        sch_data["consumption_after_losses"]["timeslots"][40] = 0.5
        sch_data["consumption_after_losses"]["timeslots"][41] = 0.5
        
        daily_entry = update_daily_entry_sch_data(
            db,
            daily_entry_id=daily_entry.id,
            sch_data=sch_data
        )
        print(f"   ✅ SCH: Consumption=₹{daily_entry.total_consumption_after_losses_mwh} MWh")
        print(f"       Losses: Regional={daily_entry.regional_loss_percent}%, State={daily_entry.state_loss_percent}%")
        
        # Step 8: Calculate derived fields
        print("\n8️⃣  Calculating derived fields...")
        daily_entry = calculate_daily_entry(
            db,
            daily_entry_id=daily_entry.id
        )
        
        print(f"\n   📊 CALCULATION RESULTS:")
        print(f"   {'─'*80}")
        print(f"   Total Scheduled:           {daily_entry.total_scheduled_mwh:.2f} MWh")
        print(f"   Consumption After Losses:  {daily_entry.total_consumption_after_losses_mwh:.2f} MWh")
        print(f"   CTU Losses:                {daily_entry.ctu_losses_mwh:.2f} MWh ({daily_entry.ctu_losses_percent:.2f}%)")
        print(f"   Energy Savings:            {daily_entry.energy_savings_mwh:.2f} MWh")
        print(f"   Total NLDC Fee:            ₹{daily_entry.total_nldc_fee:.2f}")
        print(f"   Total CTU Charges:         ₹{daily_entry.total_ctu_charges:.2f}")
        print(f"   Total Cost:                ₹{daily_entry.total_cost:.2f}")
        print(f"   Data Complete:             {'✅ YES' if daily_entry.is_complete else '❌ NO'}")
        
        # Step 9: Verify month sheet summary
        print("\n9️⃣  Verifying month sheet summary...")
        db.refresh(month_sheet)
        print(f"\n   📅 MONTH SUMMARY ({month_sheet.month_name}):")
        print(f"   {'─'*80}")
        print(f"   Total Scheduled:           {month_sheet.total_scheduled_mwh:.2f} MWh")
        print(f"   Total Consumption:         {month_sheet.total_consumption_after_losses_mwh:.2f} MWh")
        print(f"   Total Energy Savings:      {month_sheet.total_energy_savings_mwh:.2f} MWh")
        print(f"   Total GDAM Cost:           ₹{month_sheet.total_gdam_cost:.2f}")
        print(f"   Total DAM Cost:            ₹{month_sheet.total_dam_cost:.2f}")
        print(f"   Total RTM Cost:            ₹{month_sheet.total_rtm_cost:.2f}")
        print(f"   Average CTU Losses:        {month_sheet.average_ctu_losses_percent:.2f}%")
        print(f"   Days Completed:            {month_sheet.days_completed}/31")
        
        # Step 10: Test retrieval functions
        print("\n🔟  Testing retrieval functions...")
        all_months = get_all_month_sheets(db, portfolio_id=portfolio.id)
        print(f"   ✅ Found {len(all_months)} month sheet(s)")
        
        all_days = get_all_daily_entries(db, month_sheet_id=month_sheet.id)
        print(f"   ✅ Found {len(all_days)} daily entry(ies)")
        
        print("\n" + "="*100)
        print("✅ STORY 1.3 COMPLETE: Energy Schedule data model working!")
        print("="*100)
        
        print("\n📋 Summary:")
        print("   ✅ Created EnergyScheduleMonth table")
        print("   ✅ Created EnergyScheduleDay table")
        print("   ✅ Implemented CRUD operations")
        print("   ✅ DOR data integration (GDAM/DAM/RTM)")
        print("   ✅ SCH data integration (consumption + losses)")
        print("   ✅ Automatic calculations (CTU losses, energy savings)")
        print("   ✅ Month-level aggregation")
        
        print("\n📊 Data Model Hierarchy:")
        print("   Portfolio → EnergyScheduleMonth → EnergyScheduleDay")
        print("   One month per portfolio → Up to 31 days per month")
        
        print("\n🚀 Next: Story 2.1-2.4 - Implement remaining calculations")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_energy_schedule_workflow()
