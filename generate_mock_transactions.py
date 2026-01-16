#!/usr/bin/env python3
"""
Generate Mock Transaction Data for Dashboard
Creates realistic trading transactions for 14 days (Jan 1-15, 2026)
"""

import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.config import get_db
from database.models import Client, Portfolio, DailyFile, Transaction
import random

def generate_time_slots():
    """Generate 96 time slots for a day (15-minute intervals)"""
    slots = []
    for hour in range(24):
        for minute in [0, 15, 30, 45]:
            start = f"{hour:02d}:{minute:02d}"
            end_min = minute + 15
            end_hour = hour
            if end_min >= 60:
                end_min = 0
                end_hour += 1
            end = f"{end_hour:02d}:{end_min:02d}"
            slots.append(f"{start} - {end}")
    return slots

def create_mock_transactions(db: Session, start_date: datetime, days: int = 14):
    """Generate mock transactions for specified number of days"""
    
    print(f"\n🔧 Generating mock transaction data for {days} days...")
    
    # Get or create mock client
    client = db.query(Client).filter(Client.entity_id == "NPT0027").first()
    if not client:
        client = Client(
            entity_id="NPT0027",
            entity_name="Mellbro Sugars Pvt Ltd",
        )
        db.add(client)
        db.flush()
        print(f"✅ Created client: {client.entity_name}")
    else:
        print(f"✅ Found existing client: {client.entity_name}")
    
    # Get or create portfolio
    portfolio = db.query(Portfolio).filter(
        Portfolio.client_id == client.id,
        Portfolio.portfolio_code == "NPT0027_KA0"
    ).first()
    
    if not portfolio:
        portfolio = Portfolio(
            client_id=client.id,
            portfolio_code="NPT0027_KA0",
            portfolio_name="Mellbro Sugars Karnataka Portfolio",
            state="Karnataka",
            is_active=True
        )
        db.add(portfolio)
        db.flush()
        print(f"✅ Created portfolio: {portfolio.portfolio_code}")
    else:
        print(f"✅ Found existing portfolio: {portfolio.portfolio_code}")
    
    # Market types to rotate through
    market_types = ["GDAM", "DAM", "RTM"]
    report_types = ["DOR", "SCH"]
    
    time_slots = generate_time_slots()
    total_transactions = 0
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        
        print(f"\n📅 Processing {date_str}...")
        
        # Create 3-6 files per day (mix of DOR and SCH, different market types)
        num_files = random.randint(3, 6)
        
        for file_idx in range(num_files):
            report_type = random.choice(report_types)
            market_type = random.choice(market_types)
            
            # Check if file already exists
            existing_file = db.query(DailyFile).filter(
                DailyFile.portfolio_id == portfolio.id,
                DailyFile.trading_date == current_date.date(),
                DailyFile.report_type == f"{report_type}_{market_type}"
            ).first()
            
            if existing_file:
                daily_file = existing_file
                # Delete old transactions for this file to regenerate
                db.query(Transaction).filter(Transaction.daily_file_id == daily_file.id).delete()
            else:
                # Create daily file
                daily_file = DailyFile(
                    portfolio_id=portfolio.id,
                    trading_date=current_date.date(),
                    report_type=f"{report_type}_{market_type}",
                    main_category=report_type,
                    sub_category=market_type,
                    original_filename=f"MOCK_{report_type}_{market_type}_{date_str}_{portfolio.portfolio_code}.xlsx",
                    uploaded_at=datetime.now()
                )
                db.add(daily_file)
                db.flush()
            
            # Generate transactions for this file
            # DOR: mostly buy/sell transactions
            # SCH: mostly scheduling transactions
            file_transactions = 0
            
            # Create transactions for random time slots (not all 96)
            num_slots = random.randint(12, 48)  # 12-48 transactions per file
            selected_slots = random.sample(time_slots, num_slots)
            
            for time_slot in selected_slots:
                # Determine transaction type
                if report_type == "DOR":
                    # 70% buy, 30% sell for DOR
                    transaction_type = "buy" if random.random() < 0.7 else "sell"
                else:
                    # SCH is scheduling
                    transaction_type = "scheduling"
                
                # Generate realistic quantities (MW)
                if transaction_type == "scheduling":
                    quantity = round(random.uniform(0.5, 5.0), 3)
                    rate = 0.0  # Scheduling has no rate
                else:
                    quantity = round(random.uniform(0.1, 3.0), 3)
                    # Rates vary by market type
                    if market_type == "GDAM":
                        rate = round(random.uniform(2000, 3000), 2)
                    elif market_type == "DAM":
                        rate = round(random.uniform(2500, 3500), 2)
                    else:  # RTM
                        rate = round(random.uniform(2200, 4000), 2)
                
                amount = round(quantity * rate, 2)
                
                # Create transaction
                transaction = Transaction(
                    daily_file_id=daily_file.id,
                    date=current_date.date(),
                    time_slot=time_slot,
                    transaction_type=transaction_type,
                    quantity_mw=quantity,
                    rate_per_mwh=rate,
                    amount=amount,
                    solar_quantity_mw=round(quantity * random.uniform(0.1, 0.3), 3) if random.random() > 0.5 else 0.0,
                    non_solar_quantity_mw=round(quantity * random.uniform(0.7, 0.9), 3),
                    total_quantity_mw=quantity
                )
                db.add(transaction)
                file_transactions += 1
            
            total_transactions += file_transactions
            print(f"  ✓ {report_type}_{market_type}: {file_transactions} transactions")
    
    # Commit all changes
    db.commit()
    
    print(f"\n✅ Successfully generated {total_transactions} transactions across {days} days!")
    print(f"📊 Client: {client.entity_name}")
    print(f"📊 Portfolio: {portfolio.portfolio_code}")
    
    return total_transactions

def main():
    """Main execution"""
    print("=" * 80)
    print("🚀 Mock Transaction Data Generator")
    print("=" * 80)
    
    db = next(get_db())
    
    try:
        # Generate data for Jan 1-15, 2026
        start_date = datetime(2026, 1, 1)
        days = 15
        
        total = create_mock_transactions(db, start_date, days)
        
        print("\n" + "=" * 80)
        print("🎉 Mock data generation complete!")
        print("=" * 80)
        print(f"\n📈 Next steps:")
        print(f"1. Refresh your browser dashboard")
        print(f"2. Click 'Mellbro Sugars Pvt Ltd' in the sidebar")
        print(f"3. Change view modes (Hourly/Daily/Weekly/Monthly)")
        print(f"4. Change filters (DOR/SCH, GDAM/DAM/RTM)")
        print(f"\nYou should now see {total} transactions spread across {days} days!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
