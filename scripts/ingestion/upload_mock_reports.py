#!/usr/bin/env python3
"""
Upload mock trading reports to database
Uses the same upload logic as the API endpoint
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from database.config import SessionLocal, init_db
from database import services as db_services
from parsers.DOR_Parser import GDAMTemplateParser
from parsers.SCH_Parser import SCHTemplateParser

def upload_report_file(file_path: Path, db_session):
    """Upload a single report file to database"""
    try:
        filename = file_path.name
        
        # Detect parser type
        if 'SCH' in filename.upper():
            parser = SCHTemplateParser(client_id="default")
        else:
            parser = GDAMTemplateParser(client_id="default")
        
        # Parse file
        parsed_data = parser.parse_excel(str(file_path))
        metadata = parsed_data['metadata']
        
        # Get or create client
        client = db_services.get_or_create_client(
            db_session,
            entity_id=metadata.get('entity_id', 'UNKNOWN'),
            entity_name=metadata.get('entity_name', 'Unknown Entity')
        )
        
        # Get or create portfolio
        portfolio = db_services.get_or_create_portfolio(
            db_session,
            client_id=client.id,
            portfolio_code=metadata.get('portfolio_code', metadata.get('entity_id', 'DEFAULT')),
            portfolio_name=metadata.get('portfolio_name')
        )
        
        # Save daily file
        trading_date = datetime.fromisoformat(metadata['trading_date']).date() if metadata.get('trading_date') else date.today()
        delivery_date = datetime.fromisoformat(metadata['delivery_date']).date() if metadata.get('delivery_date') else trading_date
        
        daily_file = db_services.save_daily_file(
            db_session,
            portfolio_id=portfolio.id,
            trading_date=trading_date,
            delivery_date=delivery_date,
            main_category=metadata.get('main_category', 'DOR'),
            sub_category=metadata.get('sub_category', 'DAM'),
            report_type=metadata.get('report_type', 'DOR-DAM'),
            original_filename=filename,
            file_path=str(file_path),
            parsed_data=parsed_data
        )
        
        # Save transactions
        transactions_to_save = []
        if 'scheduling_transactions' in parsed_data and parsed_data['scheduling_transactions']:
            transactions_to_save = [{**txn, 'transaction_type': 'scheduling'} for txn in parsed_data['scheduling_transactions']]
        else:
            for txn in parsed_data.get('buy_transactions', []):
                transactions_to_save.append({**txn, 'transaction_type': 'buy'})
            for txn in parsed_data.get('sell_transactions', []):
                transactions_to_save.append({**txn, 'transaction_type': 'sell'})
        
        saved_transactions = db_services.save_transactions(
            db_session,
            daily_file_id=daily_file.id,
            transactions=transactions_to_save
        )
        
        print(f"  ✅ {filename}: {client.entity_name} - {saved_transactions} transactions")
        return True
        
    except Exception as e:
        print(f"  ❌ {file_path.name}: {str(e)}")
        return False

def main():
    """Upload all mock reports to database"""
    mock_reports_dir = Path(__file__).parent / "Data" / "mock_reports"
    
    if not mock_reports_dir.exists():
        print(f"❌ Mock reports directory not found: {mock_reports_dir}")
        print("   Run: python scripts/data_generation/generate_mock_reports.py")
        return False
    
    # Get all Excel files
    report_files = sorted(mock_reports_dir.glob("*.xls*"))
    
    if not report_files:
        print(f"❌ No Excel files found in {mock_reports_dir}")
        return False
    
    print(f"\n{'='*80}")
    print(f"UPLOADING {len(report_files)} MOCK REPORTS TO DATABASE")
    print(f"{'='*80}\n")
    
    # Initialize database
    print("🗄️  Initializing database...")
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        success_count = 0
        fail_count = 0
        
        for idx, file_path in enumerate(report_files, 1):
            print(f"[{idx}/{len(report_files)}] Uploading {file_path.name}...")
            if upload_report_file(file_path, db):
                success_count += 1
            else:
                fail_count += 1
        
        print(f"\n{'='*80}")
        print(f"UPLOAD COMPLETE")
        print(f"{'='*80}")
        print(f"✅ Success: {success_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"📊 Total: {len(report_files)}\n")
        
        return success_count > 0
        
    finally:
        db.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
