#!/usr/bin/env python3
"""
Check Railway Database Records
Shows total counts of Clients, Portfolios, DailyFiles (DOR/SCH), and Transactions
"""

from database.config import SessionLocal
from database.models import Client, Portfolio, DailyFile, Transaction, EnergyScheduleDay
from sqlalchemy import func

try:
    db = SessionLocal()
    
    print("\n" + "="*70)
    print("RAILWAY DATABASE RECORDS")
    print("="*70 + "\n")
    
    # Basic counts
    client_count = db.query(Client).count()
    portfolio_count = db.query(Portfolio).count()
    daily_file_count = db.query(DailyFile).count()
    transaction_count = db.query(Transaction).count()
    energy_schedule_count = db.query(EnergyScheduleDay).count()
    
    print(f"📊 Total Counts:")
    print(f"   Clients: {client_count}")
    print(f"   Portfolios: {portfolio_count}")
    print(f"   DailyFiles: {daily_file_count}")
    print(f"   Transactions: {transaction_count}")
    print(f"   Energy Schedule Days: {energy_schedule_count}")
    
    # Client details
    if client_count > 0:
        print(f"\n📋 Clients:")
        clients = db.query(Client).all()
        for client in clients:
            print(f"   - {client.entity_name} (ID: {client.entity_id})")
            
            # Count portfolios per client
            client_portfolios = db.query(Portfolio).filter(Portfolio.client_id == client.id).all()
            print(f"     Portfolios: {len(client_portfolios)}")
            for portfolio in client_portfolios:
                print(f"       • {portfolio.portfolio_code}: {portfolio.portfolio_name}")
    
    # DailyFile breakdown by report type
    if daily_file_count > 0:
        print(f"\n📄 DailyFiles by Report Type:")
        report_types = db.query(
            DailyFile.report_type, 
            func.count(DailyFile.id)
        ).group_by(DailyFile.report_type).all()
        
        for report_type, count in report_types:
            print(f"   {report_type}: {count} files")
    
    # Sample DailyFiles
    if daily_file_count > 0:
        print(f"\n📂 Sample DailyFiles (first 5):")
        sample_files = db.query(DailyFile).limit(5).all()
        for file in sample_files:
            print(f"   - {file.original_filename}")
            print(f"     Type: {file.report_type} | Date: {file.trading_date} | Portfolio: {file.portfolio.portfolio_code}")
    
    # Energy Schedule status
    if energy_schedule_count > 0:
        print(f"\n⚡ Energy Schedule Days:")
        complete_count = db.query(EnergyScheduleDay).filter(EnergyScheduleDay.is_complete == True).count()
        print(f"   Complete: {complete_count}")
        print(f"   Incomplete: {energy_schedule_count - complete_count}")
        
        # Sample complete days
        if complete_count > 0:
            print(f"\n   Sample Complete Days:")
            complete_days = db.query(EnergyScheduleDay).filter(
                EnergyScheduleDay.is_complete == True
            ).limit(3).all()
            for day in complete_days:
                print(f"   - {day.trading_date}: Scheduled {day.total_scheduled_mwh:.2f} MWh")
    
    db.close()
    print("\n" + "="*70)
    print("✅ Database connection successful!")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ Error connecting to database: {e}")
    print("\nIf you see a connection error with 'postgres.railway.internal',")
    print("you need the PUBLIC hostname from Railway dashboard:")
    print("Railway Project -> Settings -> Networking -> Public URL")
    print("\nUpdate .env file with the public hostname instead.")
