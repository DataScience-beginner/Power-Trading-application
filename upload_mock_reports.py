"""
Upload mock DOR and SCH reports to database
Processes all files in Data/mock_reports directory
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from database.config import SessionLocal
from parsers.DOR_Parser import GDAMTemplateParser
from parsers.SCH_Parser import SCHTemplateParser
from database.services import store_parsed_data

MOCK_REPORTS_DIR = "/workspaces/Power-Trading-application/Data/mock_reports"

def upload_file_to_database(filepath):
    """Upload a single file to database using appropriate parser"""
    filename = os.path.basename(filepath)
    
    try:
        # Determine file type and parser
        if 'DOR' in filename:
            parser = GDAMTemplateParser()
            report_type = "DOR"
            # Extract market type from filename
            if filename.startswith("GDAM"):
                market_type = "GDAM"
            elif filename.startswith("DAM"):
                market_type = "DAM"
            elif filename.startswith("RTM"):
                market_type = "RTM"
            else:
                market_type = "GDAM"
        elif 'SCH' in filename:
            parser = SCHTemplateParser()
            report_type = "SCH"
            market_type = "GDAM"
        else:
            print(f"  ⚠️  Skipping unknown file type: {filename}")
            return None
        
        # Parse the file
        print(f"  📄 Parsing {filename}...")
        parsed_data = parser.parse_excel(filepath)
        
        # Store in database
        db = SessionLocal()
        try:
            file_id = store_parsed_data(db, parsed_data, filename)
            print(f"  ✅ Uploaded to database (file_id: {file_id})")
            return file_id
        finally:
            db.close()
            
    except Exception as e:
        print(f"  ❌ Error uploading {filename}: {str(e)}")
        return None

def upload_all_mock_reports():
    """Upload all mock reports from the directory"""
    if not os.path.exists(MOCK_REPORTS_DIR):
        print(f"❌ Mock reports directory not found: {MOCK_REPORTS_DIR}")
        print("Run generate_mock_reports.py first!")
        return
    
    # Get all Excel files
    files = sorted([
        os.path.join(MOCK_REPORTS_DIR, f)
        for f in os.listdir(MOCK_REPORTS_DIR)
        if f.endswith(('.xlsx', '.xls'))
    ])
    
    if not files:
        print(f"❌ No Excel files found in {MOCK_REPORTS_DIR}")
        return
    
    print("=" * 80)
    print(f"UPLOADING MOCK REPORTS TO DATABASE")
    print("=" * 80)
    print(f"Found {len(files)} files to upload\n")
    
    uploaded_count = 0
    failed_count = 0
    
    for idx, filepath in enumerate(files, 1):
        print(f"\n[{idx}/{len(files)}] Processing: {os.path.basename(filepath)}")
        result = upload_file_to_database(filepath)
        
        if result:
            uploaded_count += 1
        else:
            failed_count += 1
    
    print("\n" + "=" * 80)
    print("UPLOAD SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully uploaded: {uploaded_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📊 Total: {len(files)}")
    print("=" * 80)
    
    # Verify database contents
    print("\n📊 Verifying database contents...")
    db = SessionLocal()
    try:
        from database.models import DailyFile
        from sqlalchemy import func
        
        # Count by date and type
        results = db.query(
            DailyFile.trading_date,
            DailyFile.report_type,
            DailyFile.market_type,
            func.count(DailyFile.id)
        ).group_by(
            DailyFile.trading_date,
            DailyFile.report_type,
            DailyFile.market_type
        ).order_by(DailyFile.trading_date).all()
        
        print(f"\n{'Date':<15} {'Type':<8} {'Market':<8} {'Count'}")
        print("-" * 50)
        for date, rtype, mtype, count in results:
            print(f"{date.strftime('%Y-%m-%d'):<15} {rtype:<8} {mtype:<8} {count}")
        
        print(f"\n✅ Database now contains data for calculation testing!")
        
    finally:
        db.close()

if __name__ == "__main__":
    upload_all_mock_reports()
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Restart the FastAPI backend to see updated data")
    print("2. Open the Calculate dialog in the dashboard")
    print("3. Select dates from Jan 13-22, 2026 to test calculations")
    print("4. Verify the energy schedule calculations work correctly")
    print("=" * 80)
