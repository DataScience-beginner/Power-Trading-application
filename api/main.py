"""
FastAPI Backend for Power Trading Application
Enterprise-level API with file upload and data retrieval
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path
from datetime import datetime, date
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from parsers.DOR_Parser import GDAMTemplateParser
from parsers.SCH_Parser import SCHTemplateParser
from database.config import get_db, init_db
from database import services as db_services

app = FastAPI(
    title="Power Trading Data API",
    description="Enterprise API for parsing and managing power trading data",
    version="1.0.0"
)

# CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files - check multiple possible locations
frontend_dir = Path(__file__).parent.parent / "frontend"
frontend_react_dist = Path(__file__).parent.parent / "frontend-react" / "dist"

if frontend_react_dist.exists():
    # Production: serve React build
    app.mount("/assets", StaticFiles(directory=str(frontend_react_dist / "assets")), name="assets")
elif frontend_dir.exists() and (frontend_dir / "static").exists():
    # Legacy: serve old frontend static files
    app.mount("/static", StaticFiles(directory=str(frontend_dir / "static")), name="static")

# Data storage
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database when app starts"""
    print("🗄️  Initializing database...")
    init_db()
    print("✅ Database ready")
    
    # Load mock data if database is empty
    try:
        from database.config import SessionLocal
        from database.services import get_all_clients
        
        db = SessionLocal()
        try:
            clients = get_all_clients(db)
            if len(clients) == 0:
                print("📊 Database is empty, loading mock data...")
                import subprocess
                subprocess.run(["python", "generate_mock_reports.py"], check=False)
                subprocess.run(["python", "upload_mock_reports.py"], check=False)
                print("✅ Mock data loaded")
            else:
                print(f"✅ Database has {len(clients)} clients already")
        finally:
            db.close()
    except Exception as e:
        print(f"⚠️  Mock data load failed: {e}")
        print("   You can upload files manually via the UI")

@app.get("/")
async def root():
    """Root endpoint - serves the React app"""
    react_index = Path(__file__).parent.parent / "frontend-react" / "dist" / "index.html"
    if react_index.exists():
        return FileResponse(react_index)
    
    # Fallback to old dashboard
    dashboard_file = frontend_dir / "dashboard.html"
    if dashboard_file.exists():
        return FileResponse(dashboard_file)
    
    return {
        "message": "Power Trading Analytics Dashboard",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "upload": "/api/upload",
            "analytics": "/api/analytics/summary",
            "docs": "/docs"
        }
    }

@app.get("/parser")
async def parser_ui():
    """Parser UI - simple upload and view parsed JSON"""
    html_file = frontend_dir / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "Parser UI not found"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Power Trading API"
    }

@app.post("/api/admin/reset-database")
async def reset_database(db: Session = Depends(get_db)):
    """
    ADMIN ENDPOINT: Reset database by dropping all data
    WARNING: This deletes ALL clients, portfolios, files, transactions, and calculations!
    Use this to start fresh when you need to re-upload corrected data.
    """
    from database.models import (
        Client, Portfolio, DailyFile, Transaction,
        EnergyScheduleMonth, EnergyScheduleDay, MonthlyCalculation
    )
    
    try:
        # Count records before deletion
        clients_count = db.query(Client).count()
        portfolios_count = db.query(Portfolio).count()
        files_count = db.query(DailyFile).count()
        transactions_count = db.query(Transaction).count()
        
        # Delete in reverse dependency order
        db.query(Transaction).delete()
        db.query(MonthlyCalculation).delete()
        db.query(EnergyScheduleDay).delete()
        db.query(EnergyScheduleMonth).delete()
        db.query(DailyFile).delete()
        db.query(Portfolio).delete()
        db.query(Client).delete()
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Database reset complete",
            "deleted": {
                "clients": clients_count,
                "portfolios": portfolios_count,
                "daily_files": files_count,
                "transactions": transactions_count
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database reset failed: {str(e)}"
        )

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    client_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Upload and parse Excel trading file
    
    Args:
        file: Excel file (.xls or .xlsx)
        client_id: Optional client identifier
        db: Database session (auto-injected)
        
    Returns:
        Parsed trading data in universal schema
    """
    
    # Log incoming file
    print(f"\n{'='*60}")
    print(f"📥 UPLOAD REQUEST: {file.filename}")
    print(f"Content-Type: {file.content_type}")
    print(f"Size: {file.size if hasattr(file, 'size') else 'unknown'}")
    print(f"{'='*60}\n")
    
    # Validate file type (case-insensitive)
    filename_lower = file.filename.lower()
    if not (filename_lower.endswith('.xls') or filename_lower.endswith('.xlsx')):
        print(f"❌ REJECTED: Invalid file extension for {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .xls and .xlsx files are supported."
        )
    
    print(f"✅ File type validation passed: {file.filename}")
    
    try:
        # Save uploaded file temporarily
        temp_file = OUTPUT_DIR / f"temp_{file.filename}"
        print(f"💾 Saving to temp location: {temp_file}")
        
        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        print(f"✅ File saved successfully ({len(content)} bytes)")
        
        # Detect file type and select appropriate parser
        filename_upper = file.filename.upper()
        if 'SCH' in filename_upper:
            print(f"📋 Detected SCH (Scheduling) report format")
            parser = SCHTemplateParser(client_id=client_id or "default-client")
        else:
            print(f"📋 Detected GDAM/RTM/DOR report format")
            parser = GDAMTemplateParser(client_id=client_id or "default-client")
        
        # Parse the file
        print(f"🔍 Starting parser for: {temp_file.name}")
        parsed_data = parser.parse_excel(str(temp_file))
        
        print(f"✅ Parsing completed successfully")
        print(f"   - Format: {parsed_data['metadata'].get('report_type')}")
        
        # Log transaction counts based on report type
        if 'scheduling_transactions' in parsed_data:
            print(f"   - Scheduling Transactions: {len(parsed_data['scheduling_transactions'])}")
        else:
            print(f"   - Buy Transactions: {len(parsed_data['buy_transactions'])}")
            print(f"   - Sell Transactions: {len(parsed_data['sell_transactions'])}")
        
        # Save parsed data
        output_filename = f"{Path(file.filename).stem}_parsed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file = OUTPUT_DIR / output_filename
        
        print(f"💾 Saving parsed data to: {output_filename}")
        
        with open(output_file, 'w') as f:
            json.dump(parsed_data, f, indent=2)
        
        print(f"✅ Data saved successfully\n")
        
        # ==================== SAVE TO DATABASE ====================
        print(f"\n🗄️  SAVING TO DATABASE...")
        
        metadata = parsed_data['metadata']
        
        # Step 1: Get or create client
        client = db_services.get_or_create_client(
            db,
            entity_id=metadata.get('entity_id', 'UNKNOWN'),
            entity_name=metadata.get('entity_name', 'Unknown Entity')
        )
        
        # Step 2: Get or create portfolio
        portfolio = db_services.get_or_create_portfolio(
            db,
            client_id=client.id,
            portfolio_code=metadata.get('portfolio_code', metadata.get('entity_id', 'DEFAULT')),
            portfolio_name=metadata.get('portfolio_name')
        )
        
        # Step 3: Save daily file (will REPLACE if already exists for same date+type)
        trading_date = datetime.fromisoformat(metadata['trading_date']).date() if metadata.get('trading_date') else date.today()
        delivery_date = datetime.fromisoformat(metadata['delivery_date']).date() if metadata.get('delivery_date') else trading_date
        
        daily_file = db_services.save_daily_file(
            db,
            portfolio_id=portfolio.id,
            trading_date=trading_date,
            delivery_date=delivery_date,
            main_category=metadata.get('main_category', 'DOR'),
            sub_category=metadata.get('sub_category', 'DAM'),
            report_type=metadata.get('report_type', 'DOR-DAM'),
            original_filename=file.filename,
            file_path=str(output_file),
            parsed_data=parsed_data
        )
        
        # Step 4: Save transactions
        transactions_to_save = []
        if 'scheduling_transactions' in parsed_data and parsed_data['scheduling_transactions']:
            transactions_to_save = [{**txn, 'transaction_type': 'scheduling'} for txn in parsed_data['scheduling_transactions']]
        else:
            for txn in parsed_data.get('buy_transactions', []):
                transactions_to_save.append({**txn, 'transaction_type': 'buy'})
            for txn in parsed_data.get('sell_transactions', []):
                transactions_to_save.append({**txn, 'transaction_type': 'sell'})
        
        txn_count = db_services.save_transactions(db, daily_file.id, transactions_to_save)
        
        print(f"✅ DATABASE SAVE COMPLETE:")
        print(f"   - Client: {client.entity_name}")
        print(f"   - Portfolio: {portfolio.portfolio_code}")
        print(f"   - File ID: {daily_file.id}")
        print(f"   - Transactions: {txn_count}")
        
        # ==================== STORY 3.1 & 3.2: AUTO-TRANSFER TO ENERGY SCHEDULE ====================
        energy_schedule_result = None
        try:
            from parsers.DOR_EnergySchedule_Parser import DOR_EnergyScheduleParser
            from parsers.SCH_Energy_Schedule_Parser import SCH_EnergyScheduleParser
            from database.energy_schedule_crud import (
                get_or_create_daily_entry,
                update_daily_entry_dor_data,
                update_daily_entry_sch_data,
                calculate_daily_entry
            )
            
            print(f"\n⚡ AUTO-TRANSFER TO ENERGY SCHEDULE...")
            
            # Determine if this is a DOR or SCH file
            is_dor = metadata.get('main_category') == 'DOR'
            is_sch = metadata.get('main_category') == 'SCH'
            
            if is_dor or is_sch:
                # Get or create daily entry
                daily_entry = get_or_create_daily_entry(
                    db,
                    portfolio_id=portfolio.id,
                    trading_date=trading_date
                )
                
                print(f"   ✅ Daily entry: {daily_entry.id} for {trading_date}")
                
                if is_dor:
                    # Parse with DOR Energy Schedule Parser
                    dor_parser = DOR_EnergyScheduleParser(str(temp_file))
                    dor_data = dor_parser.parse()
                    
                    market_type = metadata.get('sub_category', 'DAM')  # GDAM, DAM, or RTM
                    
                    # Update daily entry with DOR data
                    daily_entry = update_daily_entry_dor_data(
                        db,
                        daily_entry_id=daily_entry.id,
                        market_type=market_type,
                        dor_data=dor_data
                    )
                    
                    print(f"   ✅ {market_type} DOR data transferred")
                    print(f"      NLDC Fee: ₹{dor_data['summary']['nldc_application_fee']:.2f}")
                    print(f"      CTU Charges: ₹{dor_data['summary']['ctu_transmission_charges']['total']:.2f}")
                    print(f"      Total Cost: ₹{dor_data['summary']['total_cost']:.2f}")
                    
                elif is_sch:
                    # Parse with SCH Energy Schedule Parser
                    sch_parser = SCH_EnergyScheduleParser(str(temp_file))
                    sch_data = sch_parser.parse()
                    
                    # Update daily entry with SCH data
                    daily_entry = update_daily_entry_sch_data(
                        db,
                        daily_entry_id=daily_entry.id,
                        sch_data=sch_data
                    )
                    
                    print(f"   ✅ SCH consumption data transferred")
                    print(f"      Total Consumption: {sch_data['consumption_after_losses']['total_mwh']:.2f} MWh")
                    print(f"      Combined Losses: {sch_data['losses']['combined_percent']:.2f}%")
                
                # STORY 3.2: Auto-trigger calculations if all files present
                if daily_entry.has_gdam_data and daily_entry.has_dam_data and daily_entry.has_rtm_data and daily_entry.has_sch_data:
                    print(f"\n   🎯 ALL 4 FILES PRESENT - AUTO-CALCULATING...")
                    
                    daily_entry = calculate_daily_entry(db, daily_entry.id)
                    
                    print(f"   ✅ CALCULATIONS COMPLETE:")
                    print(f"      Total Scheduled: {daily_entry.total_scheduled_mwh:.2f} MWh")
                    print(f"      CTU Losses: {daily_entry.ctu_losses_mwh:.2f} MWh ({daily_entry.ctu_losses_percent:.2f}%)")
                    print(f"      Energy Savings: {daily_entry.energy_savings_mwh:.2f} MWh")
                    print(f"      Total Cost: ₹{daily_entry.total_cost:.2f}")
                    
                    energy_schedule_result = {
                        "auto_calculated": True,
                        "total_scheduled_mwh": daily_entry.total_scheduled_mwh,
                        "ctu_losses_percent": daily_entry.ctu_losses_percent,
                        "energy_savings_mwh": daily_entry.energy_savings_mwh,
                        "total_cost": daily_entry.total_cost
                    }
                else:
                    print(f"\n   ⏳ Waiting for remaining files:")
                    print(f"      GDAM: {'✅' if daily_entry.has_gdam_data else '❌'}")
                    print(f"      DAM:  {'✅' if daily_entry.has_dam_data else '❌'}")
                    print(f"      RTM:  {'✅' if daily_entry.has_rtm_data else '❌'}")
                    print(f"      SCH:  {'✅' if daily_entry.has_sch_data else '❌'}")
                    
                    energy_schedule_result = {
                        "auto_calculated": False,
                        "files_present": {
                            "gdam": daily_entry.has_gdam_data == 1,
                            "dam": daily_entry.has_dam_data == 1,
                            "rtm": daily_entry.has_rtm_data == 1,
                            "sch": daily_entry.has_sch_data == 1
                        },
                        "message": "Waiting for remaining files to auto-calculate"
                    }
                
        except Exception as e:
            print(f"\n   ⚠️  Energy Schedule transfer skipped: {str(e)}")
            energy_schedule_result = {
                "auto_calculated": False,
                "error": str(e)
            }
        
        # Clean up temp file
        temp_file.unlink()
        print(f"\n🗑️  Temp file cleaned up")
        
        return {
            "success": True,
            "message": "File parsed and saved to database successfully",
            "filename": output_filename,
            "database": {
                "client_id": client.id,
                "portfolio_id": portfolio.id,
                "file_id": daily_file.id,
                "transactions_saved": txn_count
            },
            "energy_schedule": energy_schedule_result,
            "data": parsed_data,
            "summary": {
                "trading_date": metadata.get('trading_date'),
                "delivery_date": metadata.get('delivery_date'),
                "entity": metadata.get('entity_name'),
                "portfolio": portfolio.portfolio_code,
                "report_type": metadata.get('report_type'),
                "buy_transactions": parsed_data['summary'].get('total_buy_transactions', 0),
                "sell_transactions": parsed_data['summary'].get('total_sell_transactions', 0),
                "net_amount": parsed_data['summary'].get('net_amount', 0)
            }
        }
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()
        
        # Log the full error for debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"\n{'='*60}")
        print(f"❌ ERROR: Failed to parse file {file.filename}")
        print(f"{'='*60}")
        print(error_details)
        print(f"{'='*60}\n")
        
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing file: {str(e)}. Please ensure you're uploading a valid GDAM IEX trading report in .xls or .xlsx format."
        )

@app.get("/api/files")
async def list_files():
    """List all parsed data files"""
    try:
        files = []
        for file_path in OUTPUT_DIR.glob("*_parsed_*.json"):
            stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # Sort by modified time, newest first
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return {
            "success": True,
            "count": len(files),
            "files": files
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing files: {str(e)}"
        )

@app.get("/api/data/{filename}")
async def get_data(filename: str):
    """Get parsed data by filename"""
    try:
        file_path = OUTPUT_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {filename}"
            )
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return {
            "success": True,
            "filename": filename,
            "data": data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading file: {str(e)}"
        )

@app.get("/api/summary/{filename}")
async def get_summary(filename: str):
    """Get summary of parsed data"""
    try:
        file_path = OUTPUT_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {filename}"
            )
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return {
            "success": True,
            "filename": filename,
            "metadata": data.get('metadata', {}),
            "summary": data.get('summary', {}),
            "charges": data.get('charges', {}),
            "transaction_counts": {
                "buy": len(data.get('buy_transactions', [])),
                "sell": len(data.get('sell_transactions', []))
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading file: {str(e)}"
        )

@app.delete("/api/data/{filename}")
async def delete_file(filename: str):
    """Delete a parsed data file"""
    try:
        file_path = OUTPUT_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {filename}"
            )
        
        file_path.unlink()
        
        return {
            "success": True,
            "message": f"File deleted: {filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {str(e)}"
        )


# ==================== DATABASE ENDPOINTS ====================

@app.put("/api/transactions/{transaction_id}")
async def update_transaction(
    transaction_id: int,
    updates: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    **ADMIN OVERRIDE**: Update transaction values
    
    This allows admins to manually correct any value in a time slot.
    Example: If parser got wrong quantity, admin can fix it here.
    
    Args:
        transaction_id: ID of the transaction to update
        updates: Dictionary of fields to update
            Example: {"quantity_mw": 150.5, "rate_per_mwh": 4250.0}
    """
    try:
        updated_txn = db_services.update_transaction(db, transaction_id, updates)
        
        if not updated_txn:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return {
            "success": True,
            "message": "Transaction updated successfully",
            "transaction_id": transaction_id,
            "updated_fields": list(updates.keys())
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating transaction: {str(e)}")


@app.get("/api/portfolios/{portfolio_code}/daily-files")
async def get_portfolio_daily_files(
    portfolio_code: str,
    trading_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all daily files for a portfolio.
    If date provided, returns files for that date (max 6).
    
    This shows which files are uploaded for each day.
    """
    try:
        portfolio = db_services.get_portfolio_by_code(db, portfolio_code)
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        if trading_date:
            # Get files for specific date
            date_obj = datetime.fromisoformat(trading_date).date()
            files = db_services.get_daily_files_by_date(db, portfolio.id, date_obj)
            
            return {
                "success": True,
                "portfolio": portfolio_code,
                "trading_date": trading_date,
                "file_count": len(files),
                "max_files": 6,
                "files": [
                    {
                        "id": f.id,
                        "report_type": f.report_type,
                        "main_category": f.main_category,
                        "sub_category": f.sub_category,
                        "original_filename": f.original_filename,
                        "uploaded_at": f.uploaded_at.isoformat(),
                        "transaction_count": len(f.transactions)
                    }
                    for f in files
                ]
            }
        else:
            # Get all files for portfolio
            return {
                "success": True,
                "portfolio": portfolio_code,
                "message": "Provide trading_date parameter to see files for a specific date"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching files: {str(e)}")


@app.get("/api/files/{file_id}/transactions")
async def get_file_transactions(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all transactions for a specific file.
    Returns all 96 time slots with data.
    """
    try:
        transactions = db_services.get_transactions_by_file(db, file_id)
        
        return {
            "success": True,
            "file_id": file_id,
            "transaction_count": len(transactions),
            "transactions": [
                {
                    "id": txn.id,
                    "date": txn.date.isoformat(),
                    "time_slot": txn.time_slot,
                    "transaction_type": txn.transaction_type,
                    # Buy fields
                    "quantity_mw": txn.quantity_mw,
                    "rate_per_mwh": txn.rate_per_mwh,
                    "amount": txn.amount,
                    # Sell fields  
                    "solar_quantity_mw": txn.solar_quantity_mw,
                    "non_solar_quantity_mw": txn.non_solar_quantity_mw,
                    "hydro_quantity_mw": txn.hydro_quantity_mw,
                    "total_quantity_mw": txn.total_quantity_mw,
                    # Scheduling fields
                    "regional_injection_mw": txn.regional_injection_mw,
                    "regional_drawal_mw": txn.regional_drawal_mw,
                    "regional_net_mw": txn.regional_net_mw,
                    "interface_injection_mw": txn.interface_injection_mw,
                    "interface_drawal_mw": txn.interface_drawal_mw,
                    "interface_net_mw": txn.interface_net_mw,
                    "total_losses_mw": txn.total_losses_mw
                }
                for txn in transactions
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")


@app.get("/api/clients")
async def get_clients(db: Session = Depends(get_db)):
    """Get all clients"""
    try:
        clients = db_services.get_all_clients(db)
        return {
            "success": True,
            "count": len(clients),
            "clients": [
                {
                    "id": c.id,
                    "entity_id": c.entity_id,
                    "entity_name": c.entity_name,
                    "portfolio_count": len(c.portfolios)
                }
                for c in clients
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching clients: {str(e)}")


@app.get("/api/transactions/all")
async def get_all_transactions(
    portfolio_code: str = None,
    start_date: str = None,
    end_date: str = None,
    report_type: str = None,
    db: Session = Depends(get_db)
):
    """Get all transactions with optional filters"""
    try:
        from database.models import Transaction, DailyFile, Portfolio
        from datetime import datetime
        
        query = db.query(Transaction).join(DailyFile).join(Portfolio)
        
        # Apply filters
        if portfolio_code:
            query = query.filter(Portfolio.portfolio_code == portfolio_code)
        
        if start_date:
            start = datetime.fromisoformat(start_date).date()
            query = query.filter(Transaction.date >= start)
        
        if end_date:
            end = datetime.fromisoformat(end_date).date()
            query = query.filter(Transaction.date <= end)
        
        if report_type:
            query = query.filter(DailyFile.report_type.like(f"{report_type}%"))
        
        transactions = query.order_by(Transaction.date.desc(), Transaction.time_slot).limit(1000).all()
        
        return {
            "success": True,
            "count": len(transactions),
            "transactions": [
                {
                    "id": t.id,
                    "file_id": t.daily_file_id,
                    "date": t.date.isoformat(),
                    "time_slot": t.time_slot,
                    "transaction_type": t.transaction_type,
                    "type": "BUY" if "buy" in t.transaction_type.lower() else "SELL" if "sell" in t.transaction_type.lower() else "SCHEDULE",
                    "report_type": t.daily_file.report_type,
                    "portfolio_code": t.daily_file.portfolio.portfolio_code,
                    "entity_name": t.daily_file.portfolio.client.entity_name,
                    "entity_id": t.daily_file.portfolio.client.entity_id,
                    "quantity": t.quantity_mw,
                    "quantity_mw": t.quantity_mw,
                    "rate": t.rate_per_mwh,
                    "rate_per_mwh": t.rate_per_mwh,
                    "amount": t.amount,
                    "solar_quantity_mw": t.solar_quantity_mw,
                    "non_solar_quantity_mw": t.non_solar_quantity_mw,
                    "total_quantity_mw": t.total_quantity_mw
                }
                for t in transactions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")


@app.get("/api/analytics/summary")
async def get_analytics_summary(
    portfolio_code: str = None,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Get analytics summary for dashboard"""
    try:
        from database.models import DailyFile, Transaction, Portfolio
        from sqlalchemy import func
        from datetime import datetime
        
        # Build base query
        file_query = db.query(DailyFile).join(Portfolio)
        
        if portfolio_code:
            file_query = file_query.filter(Portfolio.portfolio_code == portfolio_code)
        
        if start_date:
            start = datetime.fromisoformat(start_date).date()
            file_query = file_query.filter(DailyFile.trading_date >= start)
        
        if end_date:
            end = datetime.fromisoformat(end_date).date()
            file_query = file_query.filter(DailyFile.trading_date <= end)
        
        files = file_query.all()
        
        # Count DOR vs SCH
        dor_count = sum(1 for f in files if f.report_type.startswith('DOR'))
        sch_count = sum(1 for f in files if f.report_type.startswith('SCH'))
        
        # Get transaction stats
        txn_query = db.query(Transaction).join(DailyFile).join(Portfolio)
        
        if portfolio_code:
            txn_query = txn_query.filter(Portfolio.portfolio_code == portfolio_code)
        
        if start_date:
            txn_query = txn_query.filter(Transaction.date >= datetime.fromisoformat(start_date).date())
        
        if end_date:
            txn_query = txn_query.filter(Transaction.date <= datetime.fromisoformat(end_date).date())
        
        total_transactions = txn_query.count()
        
        # Calculate net amount
        total_amount = db.query(func.sum(Transaction.amount)).join(DailyFile).join(Portfolio)
        if portfolio_code:
            total_amount = total_amount.filter(Portfolio.portfolio_code == portfolio_code)
        if start_date:
            total_amount = total_amount.filter(Transaction.date >= datetime.fromisoformat(start_date).date())
        if end_date:
            total_amount = total_amount.filter(Transaction.date <= datetime.fromisoformat(end_date).date())
        
        net_amount = total_amount.scalar() or 0
        
        # Get hourly distribution - skip for now to avoid SQL compatibility issues
        hourly_data = []
        
        # Buy vs Sell count
        buy_count = txn_query.filter(Transaction.transaction_type == 'buy').count()
        sell_count = txn_query.filter(Transaction.transaction_type == 'sell').count()
        scheduling_count = txn_query.filter(Transaction.transaction_type == 'scheduling').count()
        
        return {
            "success": True,
            "summary": {
                "dor_files": dor_count,
                "sch_files": sch_count,
                "total_files": len(files),
                "total_transactions": total_transactions,
                "net_amount": float(net_amount),
                "buy_transactions": buy_count,
                "sell_transactions": sell_count,
                "scheduling_transactions": scheduling_count
            },
            "hourly_distribution": [
                {
                    "hour": int(h[0]) if h[0] else 0,
                    "avg_quantity": float(h[1]) if h[1] else 0
                }
                for h in hourly_data
            ] if hourly_data else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")


@app.get("/api/analytics/dor-vs-sch")
async def get_dor_vs_sch_comparison(
    portfolio_code: str = None,
    trading_date: str = None,
    db: Session = Depends(get_db)
):
    """Get DOR vs SCH comparison for same trading date"""
    try:
        from database.models import DailyFile, Transaction, Portfolio
        from datetime import datetime
        from sqlalchemy import func
        
        if not trading_date:
            raise HTTPException(status_code=400, detail="trading_date parameter required")
        
        date_obj = datetime.fromisoformat(trading_date).date()
        
        # Get DOR files for this date
        dor_query = db.query(DailyFile).join(Portfolio).filter(
            DailyFile.trading_date == date_obj,
            DailyFile.report_type.like('DOR%')
        )
        if portfolio_code:
            dor_query = dor_query.filter(Portfolio.portfolio_code == portfolio_code)
        
        # Get SCH files for this date
        sch_query = db.query(DailyFile).join(Portfolio).filter(
            DailyFile.trading_date == date_obj,
            DailyFile.report_type.like('SCH%')
        )
        if portfolio_code:
            sch_query = sch_query.filter(Portfolio.portfolio_code == portfolio_code)
        
        dor_files = dor_query.all()
        sch_files = sch_query.all()
        
        # Get hourly averages for DOR
        dor_hourly = {}
        for file in dor_files:
            transactions = db.query(Transaction).filter(Transaction.daily_file_id == file.id).all()
            for txn in transactions:
                hour = txn.time_slot.split(' - ')[0]
                if hour not in dor_hourly:
                    dor_hourly[hour] = []
                dor_hourly[hour].append(txn.quantity_mw or 0)
        
        # Get hourly averages for SCH
        sch_hourly = {}
        for file in sch_files:
            transactions = db.query(Transaction).filter(Transaction.daily_file_id == file.id).all()
            for txn in transactions:
                hour = txn.time_slot.split(' - ')[0]
                if hour not in sch_hourly:
                    sch_hourly[hour] = []
                sch_hourly[hour].append(txn.quantity_mw or txn.total_quantity_mw or 0)
        
        # Calculate averages
        dor_data = {hour: sum(vals)/len(vals) for hour, vals in dor_hourly.items()}
        sch_data = {hour: sum(vals)/len(vals) for hour, vals in sch_hourly.items()}
        
        # Generate hourly labels
        hours = sorted(set(list(dor_data.keys()) + list(sch_data.keys())))
        
        return {
            "success": True,
            "trading_date": trading_date,
            "dor_files": len(dor_files),
            "sch_files": len(sch_files),
            "comparison": {
                "hours": hours,
                "dor_values": [dor_data.get(h, 0) for h in hours],
                "sch_values": [sch_data.get(h, 0) for h in hours]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching DOR vs SCH comparison: {str(e)}")


@app.get("/api/energy-schedule/days")
async def get_energy_schedule_days(
    portfolio_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    complete_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get energy schedule days with calculations
    
    Returns list of daily energy schedule records with CTU losses, savings, costs
    """
    try:
        from database.models import EnergyScheduleDay, EnergyScheduleMonth
        
        query = db.query(EnergyScheduleDay).join(EnergyScheduleMonth)
        
        if portfolio_id:
            query = query.filter(EnergyScheduleMonth.portfolio_id == portfolio_id)
        
        if complete_only:
            query = query.filter(EnergyScheduleDay.is_complete == 1)
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(EnergyScheduleDay.trading_date >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(EnergyScheduleDay.trading_date <= end)
        
        days = query.order_by(EnergyScheduleDay.trading_date).all()
        
        result = []
        for day in days:
            result.append({
                "id": day.id,
                "trading_date": str(day.trading_date),
                "is_complete": bool(day.is_complete),
                "has_gdam": bool(day.has_gdam_data),
                "has_dam": bool(day.has_dam_data),
                "has_rtm": bool(day.has_rtm_data),
                "has_sch": bool(day.has_sch_data),
                "total_scheduled_mwh": round(day.total_scheduled_mwh, 2) if day.total_scheduled_mwh else 0,
                "ctu_losses_mwh": round(day.ctu_losses_mwh, 2) if day.ctu_losses_mwh else 0,
                "ctu_losses_percent": round(day.ctu_losses_percent, 2) if day.ctu_losses_percent else 0,
                "energy_savings_mwh": round(day.energy_savings_mwh, 2) if day.energy_savings_mwh else 0,
                "total_cost": round(day.total_cost, 2) if day.total_cost else 0,
                "total_consumption_mwh": round(day.total_consumption_after_losses_mwh, 2) if day.total_consumption_after_losses_mwh else 0
            })
        
        return {
            "success": True,
            "count": len(result),
            "days": result
        }
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/calculate/energy-schedule")
async def calculate_energy_schedule(
    request_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Calculate energy schedule using Excel template
    Uses the existing DOR/SCH parsers and Excel automation
    """
    try:
        from database.energy_schedule_service import calculator
        from datetime import date as dt_date
        
        calculation_date_str = request_data.get('calculation_date')
        print(f"🔍 Calculate request - calculation_date: {calculation_date_str}")
        
        # Parse calculation date
        if calculation_date_str:
            try:
                calc_date = datetime.fromisoformat(calculation_date_str).date()
            except:
                calc_date = datetime.strptime(calculation_date_str.split('T')[0], '%Y-%m-%d').date()
        else:
            calc_date = dt_date.today()
        
        print(f"📅 Using calculation date: {calc_date}")
        
        # Use the full Excel-based calculator
        result = calculator.calculate_energy_schedule(calc_date, db)
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error in calculate_energy_schedule: {error_details}")
        
        return {
            "success": False,
            "message": f"Calculation failed: {str(e)}",
            "error": str(e)
        }


@app.get("/api/energy-schedule/status")
async def get_energy_schedule_status(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get energy schedule calculation status for date range
    
    Args:
        start_date: Start date filter
        end_date: End date filter
        
    Returns:
        List of calculated energy schedules
    """
    try:
        from database.models import Base
        from sqlalchemy import Table, MetaData
        
        # Check if table exists
        metadata = MetaData()
        metadata.reflect(bind=db.bind)
        
        if 'energy_schedule_daily' not in metadata.tables:
            return {
                "success": True,
                "count": 0,
                "schedules": [],
                "message": "Energy schedule table not yet populated"
            }
        
        # Query energy schedules
        query = db.execute(
            "SELECT * FROM energy_schedule_daily ORDER BY calculation_date DESC LIMIT 30"
        )
        schedules = [dict(row) for row in query]
        
        return {
            "success": True,
            "count": len(schedules),
            "schedules": schedules
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching energy schedule status: {str(e)}")


# ==================== ENERGY SCHEDULE ENDPOINTS (Story 2) ====================

@app.get("/api/energy-schedule/months")
async def get_energy_schedule_months(
    portfolio_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all energy schedule month sheets
    
    Story 2.4: Energy Savings Summary - List all monthly sheets
    
    Args:
        portfolio_id: Optional portfolio filter
        
    Returns:
        List of month sheets with summary metrics
    """
    try:
        from database.energy_schedule_crud import get_all_month_sheets
        
        month_sheets = get_all_month_sheets(db, portfolio_id)
        
        result = []
        for sheet in month_sheets:
            # Calculate total NLDC fees and CTU charges from dailies
            total_nldc = 0.0
            total_ctu = 0.0
            for day in sheet.daily_entries:
                total_nldc += (day.gdam_nldc_fee or 0) + (day.dam_nldc_fee or 0) + (day.rtm_nldc_fee or 0)
                total_ctu += (day.gdam_ctu_charges or 0) + (day.dam_ctu_charges or 0) + (day.rtm_ctu_charges or 0)
            
            result.append({
                "id": sheet.id,
                "portfolio_id": sheet.portfolio_id,
                "year": sheet.year,
                "month": sheet.month,
                "month_name": sheet.month_name,
                "total_scheduled_mwh": sheet.total_scheduled_mwh,
                "total_consumption_after_losses_mwh": sheet.total_consumption_after_losses_mwh,
                "total_energy_savings": sheet.total_energy_savings_mwh,  # Frontend expects this name
                "total_gdam_cost": sheet.total_gdam_cost,
                "total_dam_cost": sheet.total_dam_cost,
                "total_rtm_cost": sheet.total_rtm_cost,
                "total_nldc_fees": total_nldc,  # Calculated from daily entries
                "total_ctu_charges": total_ctu,  # Calculated from daily entries
                "total_cost": sheet.total_gdam_cost + sheet.total_dam_cost + sheet.total_rtm_cost,  # Add total cost
                "average_ctu_losses": sheet.average_ctu_losses_percent,  # Frontend expects this name
                "total_days_completed": sheet.days_completed,  # Frontend expects this name
                "is_complete": sheet.is_complete,
                "created_at": sheet.created_at.isoformat() if sheet.created_at else None,
                "updated_at": sheet.updated_at.isoformat() if sheet.updated_at else None
            })
        
        return result  # Return array directly for frontend
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching month sheets: {str(e)}")


@app.get("/api/energy-schedule/days")
async def get_energy_schedule_days_by_date(
    portfolio_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get daily entries by date range
    
    Story 4.1: Energy Schedule View - Frontend filtering
    
    Args:
        portfolio_id: Optional portfolio filter
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        List of daily entries with calculations
    """
    try:
        from database.models import EnergyScheduleDay, EnergyScheduleMonth
        from datetime import datetime
        
        query = db.query(EnergyScheduleDay).join(EnergyScheduleMonth)
        
        if portfolio_id:
            query = query.filter(EnergyScheduleMonth.portfolio_id == portfolio_id)
        
        if start_date:
            start = datetime.fromisoformat(start_date).date()
            query = query.filter(EnergyScheduleDay.trading_date >= start)
        
        if end_date:
            end = datetime.fromisoformat(end_date).date()
            query = query.filter(EnergyScheduleDay.trading_date <= end)
        
        daily_entries = query.order_by(EnergyScheduleDay.trading_date).all()
        
        result = []
        for entry in daily_entries:
            result.append({
                "id": entry.id,
                "trading_date": entry.trading_date.isoformat(),
                "portfolio_id": entry.month_sheet.portfolio_id,
                "total_scheduled_mwh": entry.total_scheduled_mwh,
                "ctu_losses_percent": entry.ctu_losses_percent,
                "ctu_losses_mwh": entry.ctu_losses_mwh,
                "energy_savings_mwh": entry.energy_savings_mwh,
                "total_nldc_fees": entry.total_nldc_fee,  # Note: DB field is singular
                "total_ctu_charges": entry.total_ctu_charges,
                "total_cost": entry.total_cost,
                "has_gdam_data": bool(entry.has_gdam_data),  # Convert to boolean
                "has_dam_data": bool(entry.has_dam_data),
                "has_rtm_data": bool(entry.has_rtm_data),
                "has_sch_data": bool(entry.has_sch_data),
                "is_calculated": bool(entry.is_complete),  # DB field is is_complete, frontend expects is_calculated
                "calculated_at": entry.calculated_at.isoformat() if entry.calculated_at else None
            })
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching daily entries: {str(e)}")


@app.get("/api/energy-schedule/months/{month_sheet_id}/days")
async def get_energy_schedule_days_by_month(
    month_sheet_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all daily entries for a month sheet
    
    Story 2.1: CTU Losses % - Day-wise breakdown
    
    Args:
        month_sheet_id: Month sheet ID
        
    Returns:
        List of daily entries with calculations
    """
    try:
        from database.energy_schedule_crud import get_all_daily_entries
        
        daily_entries = get_all_daily_entries(db, month_sheet_id)
        
        result = []
        for entry in daily_entries:
            result.append({
                "id": entry.id,
                "trading_date": entry.trading_date.isoformat(),
                "day_of_month": entry.day_of_month,
                # DOR Data
                "gdam": {
                    "nldc_fee": entry.gdam_nldc_fee,
                    "ctu_charges": entry.gdam_ctu_charges,
                    "cost": entry.gdam_cost,
                    "scheduled_mwh": entry.gdam_scheduled_quantity_mwh
                },
                "dam": {
                    "nldc_fee": entry.dam_nldc_fee,
                    "ctu_charges": entry.dam_ctu_charges,
                    "cost": entry.dam_cost,
                    "scheduled_mwh": entry.dam_scheduled_quantity_mwh
                },
                "rtm": {
                    "nldc_fee": entry.rtm_nldc_fee,
                    "ctu_charges": entry.rtm_ctu_charges,
                    "cost": entry.rtm_cost,
                    "scheduled_mwh": entry.rtm_scheduled_quantity_mwh
                },
                # SCH Data
                "consumption_after_losses_mwh": entry.total_consumption_after_losses_mwh,
                "regional_loss_percent": entry.regional_loss_percent,
                "state_loss_percent": entry.state_loss_percent,
                "combined_loss_percent": entry.combined_loss_percent,
                # Calculated Fields
                "total_scheduled_mwh": entry.total_scheduled_mwh,
                "ctu_losses_percent": entry.ctu_losses_percent,
                "ctu_losses_mwh": entry.ctu_losses_mwh,
                "energy_savings_mwh": entry.energy_savings_mwh,
                "total_nldc_fee": entry.total_nldc_fee,
                "total_ctu_charges": entry.total_ctu_charges,
                "total_cost": entry.total_cost,
                # Completeness
                "is_complete": entry.is_complete,
                "has_gdam_data": entry.has_gdam_data,
                "has_dam_data": entry.has_dam_data,
                "has_rtm_data": entry.has_rtm_data,
                "has_sch_data": entry.has_sch_data,
                "calculated_at": entry.calculated_at.isoformat() if entry.calculated_at else None
            })
        
        return {
            "success": True,
            "count": len(result),
            "daily_entries": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching daily entries: {str(e)}")


@app.get("/api/energy-schedule/calculations/ctu-losses")
async def get_ctu_losses_analysis(
    portfolio_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get CTU Losses analysis
    
    Story 2.1: CTU Losses % Calculation
    
    Provides:
    - Day-wise CTU losses %
    - Average CTU losses for period
    - Trend analysis
    
    Args:
        portfolio_id: Optional portfolio filter
        year: Optional year filter
        month: Optional month filter
        
    Returns:
        CTU losses analysis with statistics
    """
    try:
        from database.models import EnergyScheduleDay, EnergyScheduleMonth
        
        # Build query
        query = db.query(EnergyScheduleDay).join(EnergyScheduleMonth)
        
        if portfolio_id:
            query = query.filter(EnergyScheduleMonth.portfolio_id == portfolio_id)
        if year:
            query = query.filter(EnergyScheduleMonth.year == year)
        if month:
            query = query.filter(EnergyScheduleMonth.month == month)
        
        entries = query.filter(EnergyScheduleDay.is_complete == 1).order_by(EnergyScheduleDay.trading_date).all()
        
        # Calculate statistics
        if entries:
            total_scheduled = sum(e.total_scheduled_mwh for e in entries)
            total_losses = sum(e.ctu_losses_mwh for e in entries)
            avg_ctu_losses_percent = (total_losses / total_scheduled * 100) if total_scheduled > 0 else 0
            
            daily_breakdown = []
            for entry in entries:
                daily_breakdown.append({
                    "date": entry.trading_date.isoformat(),
                    "scheduled_mwh": entry.total_scheduled_mwh,
                    "consumption_mwh": entry.total_consumption_after_losses_mwh,
                    "ctu_losses_mwh": entry.ctu_losses_mwh,
                    "ctu_losses_percent": entry.ctu_losses_percent
                })
            
            return {
                "success": True,
                "summary": {
                    "total_scheduled_mwh": total_scheduled,
                    "total_losses_mwh": total_losses,
                    "average_ctu_losses_percent": avg_ctu_losses_percent,
                    "days_analyzed": len(entries)
                },
                "daily_breakdown": daily_breakdown
            }
        else:
            return {
                "success": True,
                "summary": {
                    "total_scheduled_mwh": 0,
                    "total_losses_mwh": 0,
                    "average_ctu_losses_percent": 0,
                    "days_analyzed": 0
                },
                "daily_breakdown": [],
                "message": "No complete entries found for the specified period"
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating CTU losses: {str(e)}")


@app.get("/api/energy-schedule/calculations/ctu-charges")
async def get_ctu_charges_summary(
    portfolio_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get CTU Charges summary
    
    Story 2.2: CTU Charges Calculation
    
    Aggregates CTU transmission charges across markets:
    - GDAM CTU charges
    - DAM CTU charges
    - RTM CTU charges
    - Total CTU charges
    
    Args:
        portfolio_id: Optional portfolio filter
        year: Optional year filter
        month: Optional month filter
        
    Returns:
        CTU charges breakdown by market
    """
    try:
        from database.models import EnergyScheduleDay, EnergyScheduleMonth
        
        # Build query
        query = db.query(EnergyScheduleDay).join(EnergyScheduleMonth)
        
        if portfolio_id:
            query = query.filter(EnergyScheduleMonth.portfolio_id == portfolio_id)
        if year:
            query = query.filter(EnergyScheduleMonth.year == year)
        if month:
            query = query.filter(EnergyScheduleMonth.month == month)
        
        entries = query.filter(EnergyScheduleDay.is_complete == 1).order_by(EnergyScheduleDay.trading_date).all()
        
        # Calculate aggregates
        if entries:
            total_gdam_ctu = sum(e.gdam_ctu_charges for e in entries)
            total_dam_ctu = sum(e.dam_ctu_charges for e in entries)
            total_rtm_ctu = sum(e.rtm_ctu_charges for e in entries)
            total_ctu = sum(e.total_ctu_charges for e in entries)
            
            daily_breakdown = []
            for entry in entries:
                daily_breakdown.append({
                    "date": entry.trading_date.isoformat(),
                    "gdam_ctu_charges": entry.gdam_ctu_charges,
                    "dam_ctu_charges": entry.dam_ctu_charges,
                    "rtm_ctu_charges": entry.rtm_ctu_charges,
                    "total_ctu_charges": entry.total_ctu_charges
                })
            
            return {
                "success": True,
                "summary": {
                    "total_gdam_ctu_charges": total_gdam_ctu,
                    "total_dam_ctu_charges": total_dam_ctu,
                    "total_rtm_ctu_charges": total_rtm_ctu,
                    "total_ctu_charges": total_ctu,
                    "days_analyzed": len(entries)
                },
                "daily_breakdown": daily_breakdown
            }
        else:
            return {
                "success": True,
                "summary": {
                    "total_gdam_ctu_charges": 0,
                    "total_dam_ctu_charges": 0,
                    "total_rtm_ctu_charges": 0,
                    "total_ctu_charges": 0,
                    "days_analyzed": 0
                },
                "daily_breakdown": [],
                "message": "No complete entries found for the specified period"
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating CTU charges: {str(e)}")


@app.get("/api/energy-schedule/calculations/nldc-fees")
async def get_nldc_fees_summary(
    portfolio_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get NLDC Fees aggregation
    
    Story 2.3: NLDC Fee Aggregation
    
    Aggregates NLDC application fees across markets:
    - GDAM NLDC fees
    - DAM NLDC fees
    - RTM NLDC fees
    - Total NLDC fees
    
    Args:
        portfolio_id: Optional portfolio filter
        year: Optional year filter
        month: Optional month filter
        
    Returns:
        NLDC fees breakdown by market
    """
    try:
        from database.models import EnergyScheduleDay, EnergyScheduleMonth
        
        # Build query
        query = db.query(EnergyScheduleDay).join(EnergyScheduleMonth)
        
        if portfolio_id:
            query = query.filter(EnergyScheduleMonth.portfolio_id == portfolio_id)
        if year:
            query = query.filter(EnergyScheduleMonth.year == year)
        if month:
            query = query.filter(EnergyScheduleMonth.month == month)
        
        entries = query.filter(EnergyScheduleDay.is_complete == 1).order_by(EnergyScheduleDay.trading_date).all()
        
        # Calculate aggregates
        if entries:
            total_gdam_nldc = sum(e.gdam_nldc_fee for e in entries)
            total_dam_nldc = sum(e.dam_nldc_fee for e in entries)
            total_rtm_nldc = sum(e.rtm_nldc_fee for e in entries)
            total_nldc = sum(e.total_nldc_fee for e in entries)
            
            daily_breakdown = []
            for entry in entries:
                daily_breakdown.append({
                    "date": entry.trading_date.isoformat(),
                    "gdam_nldc_fee": entry.gdam_nldc_fee,
                    "dam_nldc_fee": entry.dam_nldc_fee,
                    "rtm_nldc_fee": entry.rtm_nldc_fee,
                    "total_nldc_fee": entry.total_nldc_fee
                })
            
            return {
                "success": True,
                "summary": {
                    "total_gdam_nldc_fees": total_gdam_nldc,
                    "total_dam_nldc_fees": total_dam_nldc,
                    "total_rtm_nldc_fees": total_rtm_nldc,
                    "total_nldc_fees": total_nldc,
                    "days_analyzed": len(entries)
                },
                "daily_breakdown": daily_breakdown
            }
        else:
            return {
                "success": True,
                "summary": {
                    "total_gdam_nldc_fees": 0,
                    "total_dam_nldc_fees": 0,
                    "total_rtm_nldc_fees": 0,
                    "total_nldc_fees": 0,
                    "days_analyzed": 0
                },
                "daily_breakdown": [],
                "message": "No complete entries found for the specified period"
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating NLDC fees: {str(e)}")


@app.get("/api/energy-schedule/calculations/energy-savings")
async def get_energy_savings_summary(
    portfolio_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get Energy Savings summary
    
    Story 2.4: Energy Savings Summary
    
    Provides comprehensive energy savings analysis:
    - Total energy savings (MWh)
    - Day-wise breakdown
    - Cost savings analysis
    - Trend data
    
    Args:
        portfolio_id: Optional portfolio filter
        year: Optional year filter
        month: Optional month filter
        
    Returns:
        Energy savings summary with detailed breakdown
    """
    try:
        from database.models import EnergyScheduleDay, EnergyScheduleMonth
        
        # Build query
        query = db.query(EnergyScheduleDay).join(EnergyScheduleMonth)
        
        if portfolio_id:
            query = query.filter(EnergyScheduleMonth.portfolio_id == portfolio_id)
        if year:
            query = query.filter(EnergyScheduleMonth.year == year)
        if month:
            query = query.filter(EnergyScheduleMonth.month == month)
        
        entries = query.filter(EnergyScheduleDay.is_complete == 1).order_by(EnergyScheduleDay.trading_date).all()
        
        # Calculate comprehensive metrics
        if entries:
            total_energy_savings = sum(e.energy_savings_mwh for e in entries)
            total_scheduled = sum(e.total_scheduled_mwh for e in entries)
            total_consumption = sum(e.total_consumption_after_losses_mwh for e in entries)
            total_cost = sum(e.total_cost for e in entries)
            
            daily_breakdown = []
            for entry in entries:
                daily_breakdown.append({
                    "date": entry.trading_date.isoformat(),
                    "scheduled_mwh": entry.total_scheduled_mwh,
                    "consumption_mwh": entry.total_consumption_after_losses_mwh,
                    "energy_savings_mwh": entry.energy_savings_mwh,
                    "ctu_losses_percent": entry.ctu_losses_percent,
                    "total_cost": entry.total_cost
                })
            
            return {
                "success": True,
                "summary": {
                    "total_energy_savings_mwh": total_energy_savings,
                    "total_scheduled_mwh": total_scheduled,
                    "total_consumption_mwh": total_consumption,
                    "total_cost": total_cost,
                    "average_savings_percent": (total_energy_savings / total_scheduled * 100) if total_scheduled > 0 else 0,
                    "days_analyzed": len(entries)
                },
                "daily_breakdown": daily_breakdown,
                "trend": {
                    "min_savings": min(e.energy_savings_mwh for e in entries),
                    "max_savings": max(e.energy_savings_mwh for e in entries),
                    "avg_savings": total_energy_savings / len(entries)
                }
            }
        else:
            return {
                "success": True,
                "summary": {
                    "total_energy_savings_mwh": 0,
                    "total_scheduled_mwh": 0,
                    "total_consumption_mwh": 0,
                    "total_cost": 0,
                    "average_savings_percent": 0,
                    "days_analyzed": 0
                },
                "daily_breakdown": [],
                "message": "No complete entries found for the specified period"
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating energy savings: {str(e)}")


# ==================== REPORT GENERATION ENDPOINTS ====================

@app.get("/api/reports/daily-trading/pdf")
async def download_daily_trading_pdf(
    date: str = None,
    portfolio_code: str = None,
    db: Session = Depends(get_db)
):
    """Generate and download PDF report for daily trading"""
    try:
        from database.models import Transaction, DailyFile, Portfolio
        from api.report_generator import generate_daily_trading_pdf
        
        query = db.query(Transaction).join(DailyFile).join(Portfolio)
        
        if date:
            query = query.filter(Transaction.date == datetime.fromisoformat(date).date())
        if portfolio_code:
            query = query.filter(Portfolio.portfolio_code == portfolio_code)
        
        transactions = query.all()
        
        trans_data = [
            {
                "date": t.date.isoformat(),
                "time_slot": t.time_slot,
                "transaction_type": t.transaction_type,
                "report_type": t.daily_file.report_type,
                "quantity_mw": t.quantity_mw,
                "rate_per_mwh": t.rate_per_mwh,
                "amount": t.amount
            }
            for t in transactions
        ]
        
        pdf_buffer = generate_daily_trading_pdf(trans_data, date or datetime.now().strftime("%Y-%m-%d"))
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=Daily_Trading_Report_{date or 'latest'}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@app.get("/api/reports/daily-trading/excel")
async def download_daily_trading_excel(
    date: str = None,
    portfolio_code: str = None,
    db: Session = Depends(get_db)
):
    """Generate and download Excel report for daily trading"""
    try:
        from database.models import Transaction, DailyFile, Portfolio
        from api.report_generator import generate_daily_trading_excel
        
        query = db.query(Transaction).join(DailyFile).join(Portfolio)
        
        if date:
            query = query.filter(Transaction.date == datetime.fromisoformat(date).date())
        if portfolio_code:
            query = query.filter(Portfolio.portfolio_code == portfolio_code)
        
        transactions = query.all()
        
        trans_data = [
            {
                "date": t.date.isoformat(),
                "time_slot": t.time_slot,
                "transaction_type": t.transaction_type,
                "report_type": t.daily_file.report_type,
                "quantity_mw": t.quantity_mw,
                "rate_per_mwh": t.rate_per_mwh,
                "amount": t.amount
            }
            for t in transactions
        ]
        
        excel_buffer = generate_daily_trading_excel(trans_data, date or datetime.now().strftime("%Y-%m-%d"))
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=Daily_Trading_Report_{date or 'latest'}.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Excel: {str(e)}")


@app.get("/api/reports/energy-schedule/pdf")
async def download_energy_schedule_pdf(
    portfolio_id: int = None,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Generate and download PDF report for energy schedule analysis"""
    try:
        from database.models import EnergyScheduleDay
        from api.report_generator import generate_energy_schedule_pdf
        
        # Query daily entries directly
        query = db.query(EnergyScheduleDay)
        
        # Filter by portfolio_id if provided
        if portfolio_id:
            from database.models import EnergyScheduleMonth
            query = query.join(EnergyScheduleMonth).filter(
                EnergyScheduleMonth.portfolio_id == portfolio_id
            )
        
        # Filter by date range
        if start_date:
            query = query.filter(EnergyScheduleDay.trading_date >= start_date)
        if end_date:
            query = query.filter(EnergyScheduleDay.trading_date <= end_date)
        
        days = query.order_by(EnergyScheduleDay.trading_date).all()
        
        days_data = [
            {
                "trading_date": day.trading_date.isoformat(),
                "energy_savings_mwh": day.energy_savings_mwh or 0,
                "ctu_losses_percent": day.ctu_losses_percent or 0,
                "total_cost": day.total_cost or 0
            }
            for day in days
        ]
        
        pdf_buffer = generate_energy_schedule_pdf(days_data)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Energy_Schedule_Report.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
