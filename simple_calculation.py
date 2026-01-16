#!/usr/bin/env python3
"""
SIMPLIFIED Energy Schedule Calculation
Just calculate CTU losses from DOR/SCH data directly - NO EXCEL
"""

from database.config import SessionLocal
from database.models import DailyFile, Transaction
from datetime import date, timedelta
from sqlalchemy import and_

def calculate_simple(calculation_date):
    """
    Simple calculation: DOR data + SCH data → CTU losses
    """
    db = SessionLocal()
    
    dor_date = calculation_date - timedelta(days=1)
    sch_date = calculation_date
    
    print(f"\n{'='*70}")
    print(f"ENERGY SCHEDULE CALCULATION - {calculation_date}")
    print(f"DOR Date: {dor_date} | SCH Date: {sch_date}")
    print(f"{'='*70}\n")
    
    # Get DOR files
    dor_files = db.query(DailyFile).filter(
        and_(
            DailyFile.trading_date == dor_date,
            DailyFile.report_type.like('DOR%')
        )
    ).all()
    
    # Get SCH files
    sch_files = db.query(DailyFile).filter(
        and_(
            DailyFile.trading_date == sch_date,
            DailyFile.report_type.like('SCH%')
        )
    ).all()
    
    print(f"Found {len(dor_files)} DOR files and {len(sch_files)} SCH files\n")
    
    if not dor_files or not sch_files:
        print("❌ Missing files!")
        return None
    
    # Calculate DOR totals (Day-ahead purchases)
    dor_total_mw = 0
    dor_total_cost = 0
    
    for dor in dor_files:
        txns = db.query(Transaction).filter(Transaction.daily_file_id == dor.id).all()
        for t in txns:
            dor_total_mw += t.quantity_mw or 0
            dor_total_cost += t.amount or 0
    
    print(f"DOR Summary:")
    print(f"  Total Purchase: {dor_total_mw:.2f} MW")
    print(f"  Total Cost: ₹{abs(dor_total_cost):,.2f}\n")
    
    # Calculate SCH totals (Scheduled delivery)
    sch_total_mw = 0
    
    for sch in sch_files:
        txns = db.query(Transaction).filter(Transaction.daily_file_id == sch.id).all()
        for t in txns:
            sch_total_mw += t.quantity_mw or 0
    
    print(f"SCH Summary:")
    print(f"  Total Scheduled: {sch_total_mw:.2f} MW\n")
    
    # Calculate CTU Losses (3.43% standard)
    CTU_LOSS_PCT = 3.43
    ctu_losses_mw = dor_total_mw * (CTU_LOSS_PCT / 100)
    energy_after_losses_mw = dor_total_mw - ctu_losses_mw
    
    # Energy savings (if scheduled < purchased after losses)
    energy_saved_mw = energy_after_losses_mw - sch_total_mw
    
    # Cost per MW
    cost_per_mw = abs(dor_total_cost) / dor_total_mw if dor_total_mw > 0 else 0
    cost_savings = energy_saved_mw * cost_per_mw
    
    print(f"{'='*70}")
    print(f"CALCULATION RESULTS:")
    print(f"{'='*70}")
    print(f"Total Purchased (DOR): {dor_total_mw:.2f} MW")
    print(f"CTU Losses ({CTU_LOSS_PCT}%): {ctu_losses_mw:.2f} MW")
    print(f"After Losses: {energy_after_losses_mw:.2f} MW")
    print(f"Total Scheduled (SCH): {sch_total_mw:.2f} MW")
    print(f"Energy Saved: {energy_saved_mw:.2f} MW")
    print(f"Total Cost: ₹{abs(dor_total_cost):,.2f}")
    print(f"Cost Savings: ₹{abs(cost_savings):,.2f}")
    print(f"{'='*70}\n")
    
    db.close()
    
    return {
        "success": True,
        "calculation_date": str(calculation_date),
        "dor_date": str(dor_date),
        "sch_date": str(sch_date),
        "total_purchased_mw": round(dor_total_mw, 2),
        "ctu_losses_mw": round(ctu_losses_mw, 2),
        "ctu_losses_pct": CTU_LOSS_PCT,
        "energy_after_losses_mw": round(energy_after_losses_mw, 2),
        "total_scheduled_mw": round(sch_total_mw, 2),
        "energy_saved_mw": round(energy_saved_mw, 2),
        "total_cost_inr": round(abs(dor_total_cost), 2),
        "cost_savings_inr": round(abs(cost_savings), 2)
    }

if __name__ == "__main__":
    # Test for Jan 2, 2026
    result = calculate_simple(date(2026, 1, 2))
    
    if result:
        print("✅ Calculation successful!")
        print(f"   Energy Saved: {result['energy_saved_mw']} MW")
        print(f"   Cost Savings: ₹{result['cost_savings_inr']:,.2f}")
