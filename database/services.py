"""
Database Service Layer

This file contains all database operations (CRUD - Create, Read, Update, Delete).
Instead of writing SQL directly in API routes, we use these service functions.

Benefits:
- Cleaner code
- Reusable functions
- Easier testing
- Business logic in one place
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.models import Client, Portfolio, DailyFile, Transaction, MonthlyCalculation
from datetime import date, datetime
from typing import List, Optional, Dict, Any
import json


# ==================== CLIENT OPERATIONS ====================

def get_or_create_client(db: Session, entity_id: str, entity_name: str) -> Client:
    """
    Get existing client or create new one.
    This ensures we don't create duplicate clients.
    """
    client = db.query(Client).filter(Client.entity_id == entity_id).first()
    
    if not client:
        client = Client(
            entity_id=entity_id,
            entity_name=entity_name
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        print(f"✅ Created new client: {entity_name} ({entity_id})")
    
    return client


def get_all_clients(db: Session) -> List[Client]:
    """Get all clients"""
    return db.query(Client).all()


# ==================== PORTFOLIO OPERATIONS ====================

def get_or_create_portfolio(db: Session, client_id: int, portfolio_code: str, portfolio_name: str = None) -> Portfolio:
    """
    Get existing portfolio or create new one
    """
    portfolio = db.query(Portfolio).filter(Portfolio.portfolio_code == portfolio_code).first()
    
    if not portfolio:
        portfolio = Portfolio(
            client_id=client_id,
            portfolio_code=portfolio_code,
            portfolio_name=portfolio_name or portfolio_code
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
        print(f"✅ Created new portfolio: {portfolio_code}")
    
    return portfolio


def get_portfolio_by_code(db: Session, portfolio_code: str) -> Optional[Portfolio]:
    """Get portfolio by code"""
    return db.query(Portfolio).filter(Portfolio.portfolio_code == portfolio_code).first()


# ==================== DAILY FILE OPERATIONS ====================

def save_daily_file(
    db: Session,
    portfolio_id: int,
    trading_date: date,
    delivery_date: date,
    main_category: str,
    sub_category: str,
    report_type: str,
    original_filename: str,
    file_path: str,
    parsed_data: Dict[str, Any]
) -> DailyFile:
    """
    Save or UPDATE daily file to database.
    
    KEY LOGIC: If file already exists for this portfolio + date + type,
    it will be REPLACED (not duplicated).
    
    This ensures max 6 files per portfolio per day.
    """
    
    # Check if file already exists
    existing_file = db.query(DailyFile).filter(
        and_(
            DailyFile.portfolio_id == portfolio_id,
            DailyFile.trading_date == trading_date,
            DailyFile.report_type == report_type
        )
    ).first()
    
    if existing_file:
        print(f"⚠️  File already exists: {report_type} for {trading_date}")
        print(f"🔄 REPLACING old file (ID: {existing_file.id})")
        
        # Delete old transactions
        db.query(Transaction).filter(Transaction.daily_file_id == existing_file.id).delete()
        
        # Update existing file
        existing_file.delivery_date = delivery_date
        existing_file.main_category = main_category
        existing_file.sub_category = sub_category
        existing_file.original_filename = original_filename
        existing_file.file_path = file_path
        existing_file.summary = parsed_data.get('summary', {})
        existing_file.charges = parsed_data.get('charges', {})
        existing_file.file_metadata = parsed_data.get('metadata', {})
        existing_file.parsed_at = datetime.now()
        existing_file.uploaded_at = datetime.now()
        
        db.commit()
        db.refresh(existing_file)
        
        daily_file = existing_file
        print(f"✅ Updated existing file")
        
    else:
        # Create new file
        daily_file = DailyFile(
            portfolio_id=portfolio_id,
            trading_date=trading_date,
            delivery_date=delivery_date,
            main_category=main_category,
            sub_category=sub_category,
            report_type=report_type,
            original_filename=original_filename,
            file_path=file_path,
            summary=parsed_data.get('summary', {}),
            charges=parsed_data.get('charges', {}),
            file_metadata=parsed_data.get('metadata', {}),
            parsed_at=datetime.now()
        )
        
        db.add(daily_file)
        db.commit()
        db.refresh(daily_file)
        print(f"✅ Created new file: {report_type} for {trading_date}")
    
    return daily_file


def get_daily_files_by_date(db: Session, portfolio_id: int, trading_date: date) -> List[DailyFile]:
    """
    Get all files for a specific portfolio and date.
    Should return max 6 files.
    """
    return db.query(DailyFile).filter(
        and_(
            DailyFile.portfolio_id == portfolio_id,
            DailyFile.trading_date == trading_date
        )
    ).all()


def get_daily_file_by_id(db: Session, file_id: int) -> Optional[DailyFile]:
    """Get specific file by ID"""
    return db.query(DailyFile).filter(DailyFile.id == file_id).first()


# ==================== TRANSACTION OPERATIONS ====================

def save_transactions(db: Session, daily_file_id: int, transactions: List[Dict[str, Any]]) -> int:
    """
    Save all transactions for a file.
    Returns count of transactions saved.
    """
    count = 0
    
    for txn_data in transactions:
        transaction = Transaction(
            daily_file_id=daily_file_id,
            date=datetime.fromisoformat(txn_data['date']).date(),
            time_slot=txn_data.get('time_slot'),
            time_block_start=datetime.fromisoformat(txn_data['time_block_start']),
            time_block_end=datetime.fromisoformat(txn_data['time_block_end']),
            transaction_type=txn_data.get('transaction_type', 'unknown'),
            
            # Buy fields
            quantity_mw=txn_data.get('quantity_mw', 0.0),
            rate_per_mwh=txn_data.get('rate_per_mwh', 0.0),
            amount=txn_data.get('amount', 0.0),
            
            # Sell fields
            solar_quantity_mw=txn_data.get('solar_quantity_mw', 0.0),
            non_solar_quantity_mw=txn_data.get('non_solar_quantity_mw', 0.0),
            hydro_quantity_mw=txn_data.get('hydro_quantity_mw', 0.0),
            total_quantity_mw=txn_data.get('total_quantity_mw', 0.0),
            
            # Scheduling fields
            regional_injection_mw=txn_data.get('regional_injection_mw', 0.0),
            regional_drawal_mw=txn_data.get('regional_drawal_mw', 0.0),
            regional_net_mw=txn_data.get('regional_net_mw', 0.0),
            interface_injection_mw=txn_data.get('interface_injection_mw', 0.0),
            interface_drawal_mw=txn_data.get('interface_drawal_mw', 0.0),
            interface_net_mw=txn_data.get('interface_net_mw', 0.0),
            injection_losses_mw=txn_data.get('injection_losses_mw', 0.0),
            drawal_losses_mw=txn_data.get('drawal_losses_mw', 0.0),
            total_losses_mw=txn_data.get('total_losses_mw', 0.0),
            net_scheduled_mw=txn_data.get('net_scheduled_mw', 0.0)
        )
        
        db.add(transaction)
        count += 1
    
    db.commit()
    print(f"✅ Saved {count} transactions")
    
    return count


def get_transactions_by_file(db: Session, file_id: int) -> List[Transaction]:
    """Get all transactions for a specific file"""
    return db.query(Transaction).filter(Transaction.daily_file_id == file_id).order_by(Transaction.time_block_start).all()


def update_transaction(db: Session, transaction_id: int, updates: Dict[str, Any]) -> Optional[Transaction]:
    """
    Update specific transaction fields (ADMIN OVERRIDE).
    
    This is used when admin wants to manually correct a value.
    
    Example:
        updates = {
            'quantity_mw': 150.5,
            'rate_per_mwh': 4250.0
        }
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        return None
    
    # Update only provided fields
    for key, value in updates.items():
        if hasattr(transaction, key):
            setattr(transaction, key, value)
    
    db.commit()
    db.refresh(transaction)
    
    print(f"✅ Updated transaction {transaction_id}: {updates}")
    
    return transaction


# ==================== ANALYTICS QUERIES ====================

def get_portfolio_summary(db: Session, portfolio_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
    """
    Get summary analytics for a portfolio over a date range.
    Useful for dashboards and reports.
    """
    files = db.query(DailyFile).filter(
        and_(
            DailyFile.portfolio_id == portfolio_id,
            DailyFile.trading_date >= start_date,
            DailyFile.trading_date <= end_date
        )
    ).all()
    
    total_files = len(files)
    dor_files = sum(1 for f in files if f.main_category == 'DOR')
    sch_files = sum(1 for f in files if f.main_category == 'SCH')
    
    return {
        'total_files': total_files,
        'dor_files': dor_files,
        'sch_files': sch_files,
        'date_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        }
    }


# ==================== MONTHLY CALCULATION OPERATIONS ====================

def save_monthly_calculation(
    db: Session,
    portfolio_id: int,
    calculation_date: date,
    calculation_type: str,
    calculation_data: Dict[str, Any],
    metrics: Dict[str, float] = None
) -> MonthlyCalculation:
    """
    Save or update monthly calculation result.
    This stores the results from your predefined Excel calculation sheet.
    """
    
    # Check if calculation already exists
    existing = db.query(MonthlyCalculation).filter(
        and_(
            MonthlyCalculation.portfolio_id == portfolio_id,
            MonthlyCalculation.calculation_date == calculation_date,
            MonthlyCalculation.calculation_type == calculation_type
        )
    ).first()
    
    if existing:
        # Update existing
        existing.calculation_data = calculation_data
        if metrics:
            for key, value in metrics.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
        existing.updated_at = datetime.now()
        db.commit()
        db.refresh(existing)
        return existing
    
    else:
        # Create new
        calc = MonthlyCalculation(
            portfolio_id=portfolio_id,
            year=calculation_date.year,
            month=calculation_date.month,
            day=calculation_date.day,
            calculation_date=calculation_date,
            calculation_type=calculation_type,
            calculation_data=calculation_data,
            **(metrics or {})
        )
        db.add(calc)
        db.commit()
        db.refresh(calc)
        return calc


def get_monthly_calculations(db: Session, portfolio_id: int, year: int, month: int) -> List[MonthlyCalculation]:
    """Get all calculations for a specific month"""
    return db.query(MonthlyCalculation).filter(
        and_(
            MonthlyCalculation.portfolio_id == portfolio_id,
            MonthlyCalculation.year == year,
            MonthlyCalculation.month == month
        )
    ).order_by(MonthlyCalculation.day).all()
