#!/usr/bin/env python3
"""
Upload 7-Day Mock Data to Railway PostgreSQL
=============================================

Clears existing Railway database and uploads fresh 7-day mock data.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from database.config import SessionLocal, engine
from database.models import Base, Client, Portfolio, DailyFile, Transaction, EnergyScheduleDay, EnergyScheduleMonth
from parsers.DOR_Parser import GDAMTemplateParser
from parsers.SCH_Parser import SCHTemplateParser
from database import services as db_services

MOCK_DATA_DIR = Path("mock_data_7days")


def clear_railway_database():
    """Clear all data from Railway database (but keep tables)"""
    print("\n" + "="*70)
    print("CLEARING RAILWAY DATABASE")
    print("="*70 + "\n")
    
    db = SessionLocal()
    try:
        # Delete in correct order (children first)
        transaction_count = db.query(Transaction).count()
        db.query(Transaction).delete()
        print(f"✅ Deleted {transaction_count} transactions")
        
        energy_schedule_count = db.query(EnergyScheduleDay).count()
        db.query(EnergyScheduleDay).delete()
        print(f"✅ Deleted {energy_schedule_count} energy schedule days")
        
        # Delete energy schedule months (parent of schedule days)
        month_count = db.query(EnergyScheduleMonth).count()
        db.query(EnergyScheduleMonth).delete()
        print(f"✅ Deleted {month_count} energy schedule months")
        
        daily_file_count = db.query(DailyFile).count()
        db.query(DailyFile).delete()
        print(f"✅ Deleted {daily_file_count} daily files")
        
        portfolio_count = db.query(Portfolio).count()
        db.query(Portfolio).delete()
        print(f"✅ Deleted {portfolio_count} portfolios")
        
        client_count = db.query(Client).count()
        db.query(Client).delete()
        print(f"✅ Deleted {client_count} clients")
        
        db.commit()
        print("\n✅ Database cleared successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error clearing database: {e}")
        raise
    finally:
        db.close()


def upload_mock_files_to_railway():
    """Upload all mock files to Railway database"""
    
    print("\n" + "="*70)
    print("UPLOADING MOCK DATA TO RAILWAY")
    print("="*70 + "\n")
    
    # Check if mock data directory exists
    if not MOCK_DATA_DIR.exists():
        print(f"❌ Mock data directory not found: {MOCK_DATA_DIR}")
        print("   Run: python generate_7day_mock_data.py first!")
        return
    
    # Get all Excel files
    excel_files = list(MOCK_DATA_DIR.glob("*.xlsx")) + list(MOCK_DATA_DIR.glob("*.xls"))
    
    if not excel_files:
        print(f"❌ No Excel files found in {MOCK_DATA_DIR}")
        return
    
    print(f"Found {len(excel_files)} files to upload\n")
    
    # Sort files: DOR files first (for each date), then SCH files
    dor_files = sorted([f for f in excel_files if 'DOR' in f.name])
    sch_files = sorted([f for f in excel_files if 'SCH' in f.name])
    sorted_files = dor_files + sch_files
    
    db = SessionLocal()
    success_count = 0
    error_count = 0
    
    for idx, file_path in enumerate(sorted_files, 1):
        try:
            print(f"[{idx}/{len(sorted_files)}] Processing: {file_path.name}")
            
            # Detect file type
            if 'DOR' in file_path.name:
                parser = GDAMTemplateParser()
                parsed_data = parser.parse_excel(str(file_path))
            elif 'SCH' in file_path.name:
                parser = SCHTemplateParser()
                parsed_data = parser.parse_excel(str(file_path))
            else:
                print(f"    ⚠️  Skipped: Unknown file type")
                continue
            
            # Extract metadata
            metadata = parsed_data['metadata']
            entity_id = metadata.get('entity_id', 'UNKNOWN')
            entity_name = metadata.get('entity_name', 'Unknown Client')
            portfolio_code = metadata.get('portfolio_code', 'UNKNOWN')
            portfolio_name = metadata.get('portfolio_name', portfolio_code)
            
            # Get or create client
            client = db_services.get_or_create_client(
                db, 
                entity_id=entity_id,
                entity_name=entity_name
            )
            
            # Get or create portfolio
            portfolio = db_services.get_or_create_portfolio(
                db,
                client_id=client.id,
                portfolio_code=portfolio_code,
                portfolio_name=portfolio_name
            )
            
            # Save daily file with transactions
            daily_file = db_services.save_daily_file(
                db,
                portfolio_id=portfolio.id,
                parsed_data=parsed_data,
                original_filename=file_path.name,
                file_path=str(file_path)
            )
            
            print(f"    ✅ Uploaded: {metadata.get('report_type', 'Unknown')} for {metadata.get('trading_date', 'Unknown date')}")
            success_count += 1
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            error_count += 1
            db.rollback()
            continue
    
    db.close()
    
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"\n✅ Successfully uploaded: {success_count} files")
    print(f"❌ Errors: {error_count} files")
    
    # Show final database stats
    print("\n" + "="*70)
    print("FINAL DATABASE STATUS")
    print("="*70 + "\n")
    
    db = SessionLocal()
    print(f"Clients: {db.query(Client).count()}")
    print(f"Portfolios: {db.query(Portfolio).count()}")
    print(f"DailyFiles: {db.query(DailyFile).count()}")
    print(f"Transactions: {db.query(Transaction).count()}")
    
    # Show file breakdown
    print(f"\nFile Types:")
    from sqlalchemy import func
    file_types = db.query(
        DailyFile.report_type,
        func.count(DailyFile.id)
    ).group_by(DailyFile.report_type).all()
    
    for report_type, count in file_types:
        print(f"   {report_type}: {count}")
    
    db.close()
    
    print("\n" + "="*70)
    print("✅ Upload to Railway complete!")
    print("="*70 + "\n")


def main():
    """Main execution"""
    
    print("\n" + "="*70)
    print("RAILWAY DATABASE RESET & UPLOAD")
    print("="*70)
    print("\nThis will:")
    print("1. Clear all existing data from Railway database")
    print("2. Upload 7 days of fresh mock data")
    print("\n⚠️  WARNING: This will delete ALL existing data!")
    
    response = input("\nContinue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Operation cancelled.")
        return
    
    try:
        # Step 1: Clear database
        clear_railway_database()
        
        # Step 2: Upload mock data
        upload_mock_files_to_railway()
        
        print("\n✅ All operations completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Operation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
