"""
Energy Platform Integration Module
Integrates the excel-consumption-service as a sub-router under the main API.

This allows clients to use a single URL for all features:
- DOR/SCH file upload → Main app (/api/upload)
- Workbook upload → Energy Platform (/api/v1/workbooks/upload)
- Authentication → Energy Platform (/api/v1/auth/*)
"""

import sys
from pathlib import Path

# Add energy-platform to Python path
ENERGY_PLATFORM_PATH = Path(__file__).parent.parent / "energy-platform" / "services" / "excel-consumption-service" / "src"
sys.path.insert(0, str(ENERGY_PLATFORM_PATH))

from fastapi import APIRouter
from excel_consumption_service.api.routes.auth import router as auth_router
from excel_consumption_service.api.routes.workbooks import router as workbook_router
from excel_consumption_service.core.config import get_settings
from excel_consumption_service.db.session import engine, SessionLocal
from excel_consumption_service.models.base import Base
from excel_consumption_service.models import *  # Ensure all models are loaded
from excel_consumption_service.db.bootstrap import seed_reference_data

# Create a combined router for energy platform endpoints
# IMPORTANT: We exclude the system router (/) to avoid overriding main app's root
energy_router = APIRouter()
energy_router.include_router(auth_router)
energy_router.include_router(workbook_router)

def init_energy_platform_db():
    """Initialize the energy platform database tables."""
    print("Initializing Energy Platform database...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Seed reference data (tenants, roles, admin user)
    db = SessionLocal()
    try:
        seed_reference_data(db)
        print("Energy Platform database ready")
    except Exception as e:
        print(f"Seed data error (may already exist): {e}")
    finally:
        db.close()

def get_energy_platform_routes():
    """Return the energy platform router for mounting."""
    return energy_router