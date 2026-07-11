#!/usr/bin/env python3
"""
Direct Database Insert - 7 Days Mock Data
==========================================

Bypasses Excel parsing and inserts mock data directly into Railway PostgreSQL.
Creates realistic DOR and SCH trading data for 7 consecutive days.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from random import uniform, choice

sys.path.append(str(Path(__file__).parent))

from database.config import SessionLocal
from database.models import Client, Portfolio, DailyFile, Transaction
import json

# Configuration
START_DATE = datetime(2026, 1, 10)
NUM_DAYS = 7

CLIENT_DATA = {
    "entity_id": "A2AR0NPT0027",
    "entity_name": "Grasim Industries Limited",
    "portfolio_code": "NPT0019_TN0",
    "portfolio_name": "Grasim Industries Limited - Tamil Nadu"
}


def clear_database(db):
    """Clear existing data"""
    print("\n🗑️  Clearing existing data...")
    db.query(Transaction).delete()
    db.query(DailyFile).delete()
    db.query(Portfolio).delete()
    db.query(Client).delete()
    db.commit()
    print("✅ Database cleared")


def create_client_and_portfolio(db):
    """Create or get client and portfolio"""
    print(f"\n👤 Creating client: {CLIENT_DATA['entity_name']}")
    
    client = Client(
        entity_id=CLIENT_DATA['entity_id'],
        entity_name=CLIENT_DATA['entity_name']
    )
    db.add(client)
    db.flush()
    
    portfolio = Portfolio(
        client_id=client.id,
        portfolio_code=CLIENT_DATA['portfolio_code'],
        portfolio_name=CLIENT_DATA['portfolio_name']
    )
    db.add(portfolio)
    db.flush()
    
    print(f"✅ Client ID: {client.id}, Portfolio ID: {portfolio.id}")
    return client, portfolio


def generate_timeslot_transactions(trading_date, report_type, main_category):
    """Generate 96 timeslot transactions (15-min intervals)"""
    transactions = []
    
    for hour in range(24):
        for minute in [0, 15, 30, 45]:
            start_time = f"{hour:02d}:{minute:02d}"
            end_minute = minute + 15
            end_hour = hour
            if end_minute == 60:
                end_minute = 0
                end_hour = (hour + 1) % 24
            end_time = f"{end_hour:02d}:{end_minute:02d}"
            time_slot = f"{start_time} - {end_time}"
            
            # Create datetime for time block
            time_block_start = datetime.combine(trading_date.date(), datetime.strptime(start_time, "%H:%M").time())
            time_block_end = datetime.combine(trading_date.date(), datetime.strptime(end_time, "%H:%M").time())
            if end_hour < hour:  # Crossed midnight
                time_block_end += timedelta(days=1)
            
            if main_category == "DOR":
                # DOR has buy transactions
                buy_qty = round(uniform(5, 50), 2) if uniform(0, 1) > 0.3 else 0
                transactions.append({
                    "transaction_type": "buy",
                    "time_slot": time_slot,
                    "time_block_start": time_block_start,
                    "time_block_end": time_block_end,
                    "date": trading_date.date(),
                    "quantity_mw": buy_qty,
                    "rate_per_mwh": round(uniform(3.5, 5.5), 2),
                    "amount": buy_qty * round(uniform(3.5, 5.5), 2)
                })
                # DOR has sell transactions
                sell_qty = round(uniform(2, 30), 2) if uniform(0, 1) > 0.4 else 0
                transactions.append({
                    "transaction_type": "sell",
                    "time_slot": time_slot,
                    "time_block_start": time_block_start,
                    "time_block_end": time_block_end,
                    "date": trading_date.date(),
                    "total_quantity_mw": sell_qty,
                    "solar_quantity_mw": sell_qty * 0.6,
                    "non_solar_quantity_mw": sell_qty * 0.4
                })
            else:  # SCH
                # SCH has scheduling transactions
                reg_inj = round(uniform(10, 80), 2)
                reg_draw = round(uniform(10, 80), 2)
                transactions.append({
                    "transaction_type": "scheduling",
                    "time_slot": time_slot,
                    "time_block_start": time_block_start,
                    "time_block_end": time_block_end,
                    "date": trading_date.date(),
                    "regional_injection_mw": reg_inj,
                    "regional_drawal_mw": reg_draw,
                    "regional_net_mw": reg_inj - reg_draw,
                    "interface_injection_mw": round(uniform(5, 40), 2),
                    "interface_drawal_mw": round(uniform(5, 40), 2)
                })
    
    return transactions


def create_daily_files(db, portfolio, trading_date):
    """Create 6 daily files (3 DOR + 3 SCH) for one day"""
    date_str = trading_date.strftime("%Y-%m-%d")
    delivery_date = trading_date + timedelta(days=1)
    
    print(f"\n📅 {date_str}")
    
    report_types = [
        ("DOR", "GDAM"),
        ("DOR", "DAM"),
        ("DOR", "RTM"),
        ("SCH", "GDAM"),
        ("SCH", "DAM"),
        ("SCH", "RTM")
    ]
    
    files_created = 0
    trans_created = 0
    
    for main_cat, sub_cat in report_types:
        report_type = f"{main_cat}-{sub_cat}"
        
        # Create DailyFile
        daily_file = DailyFile(
            portfolio_id=portfolio.id,
            trading_date=trading_date.date(),
            delivery_date=delivery_date.date() if main_cat == "DOR" else None,
            main_category=main_cat,
            sub_category=sub_cat,
            report_type=report_type,
            original_filename=f"{sub_cat}_Mock_{date_str.replace('-', '')}_{report_type}.xlsx",
            file_path=f"/mock/{report_type}_{date_str}.xlsx",
            summary=json.dumps({
                "total_buy_mwh": round(uniform(500, 2000), 2) if main_cat == "DOR" else 0,
                "total_sell_mwh": round(uniform(300, 1500), 2) if main_cat == "DOR" else 0,
                "total_scheduled_mwh": round(uniform(1000, 3000), 2) if main_cat == "SCH" else 0
            }),
            charges=json.dumps({
                "nldc_fee": round(uniform(1000, 5000), 2),
                "ctu_charges": round(uniform(10000, 50000), 2),
                "other_charges": round(uniform(500, 2000), 2)
            }) if main_cat == "DOR" else None,
            parsed_at=datetime.now()
        )
        db.add(daily_file)
        db.flush()
        
        # Generate transactions
        transactions_data = generate_timeslot_transactions(trading_date, report_type, main_cat)
        
        for trans_data in transactions_data:
            transaction = Transaction(
                daily_file_id=daily_file.id,
                **trans_data  # Unpack the dict with correct field names
            )
            db.add(transaction)
            trans_created += 1
        
        files_created += 1
        print(f"   ✅ {report_type}: {len(transactions_data)} transactions")
    
    db.commit()
    return files_created, trans_created


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("DIRECT DATABASE INSERT - 7-DAY MOCK DATA")
    print("="*70)
    print(f"\nDate range: {START_DATE.strftime('%Y-%m-%d')} to {(START_DATE + timedelta(days=NUM_DAYS-1)).strftime('%Y-%m-%d')}")
    print(f"Client: {CLIENT_DATA['entity_name']}")
    
    response = input("\n⚠️  This will CLEAR all existing data. Continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Operation cancelled.")
        return
    
    db = SessionLocal()
    
    try:
        # Clear database
        clear_database(db)
        
        # Create client and portfolio
        client, portfolio = create_client_and_portfolio(db)
        
        # Generate data for each day
        total_files = 0
        total_transactions = 0
        
        for day_offset in range(NUM_DAYS):
            trading_date = START_DATE + timedelta(days=day_offset)
            files, trans = create_daily_files(db, portfolio, trading_date)
            total_files += files
            total_transactions += trans
        
        print("\n" + "="*70)
        print("UPLOAD COMPLETE!")
        print("="*70)
        print(f"\n✅ Created:")
        print(f"   Clients: 1")
        print(f"   Portfolios: 1")
        print(f"   DailyFiles: {total_files} (6 per day × {NUM_DAYS} days)")
        print(f"   Transactions: {total_transactions}")
        
        # Verify
        print(f"\n📊 Database verification:")
        print(f"   Clients: {db.query(Client).count()}")
        print(f"   Portfolios: {db.query(Portfolio).count()}")
        print(f"   DailyFiles: {db.query(DailyFile).count()}")
        print(f"   Transactions: {db.query(Transaction).count()}")
        
        print("\n✅ All data successfully loaded into Railway PostgreSQL!")
        print("="*70 + "\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
