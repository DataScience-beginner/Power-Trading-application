
"""
FastAPI Backend for Power Trading Application
Enterprise-level API with file upload and data retrieval
Version: 1.0.1
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Body, Header
from database.config import get_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path
from datetime import datetime, date
import sys
from io import BytesIO
from uuid import uuid4
import re

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))



# --- Admin Database Tree Endpoints ---
from sqlalchemy import inspect, text

# ...existing code...

# Place admin endpoints after get_current_admin definition

# ...existing code...

# JWT and Auth imports

# JWT and Auth imports
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta
from openpyxl import load_workbook

# JWT Config
SECRET_KEY = "your-very-secret-key"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    if token_data.username != ADMIN_USERNAME:
        raise credentials_exception
    return {"username": token_data.username}

# JWT and Auth imports
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta

from parsers.DOR_Parser import GDAMTemplateParser
from parsers.SCH_Parser import SCHTemplateParser
from database.config import get_db, init_db
from database import services as db_services
from database.models import WorkbookUploadRecord, WorkbookResultRow
from api.routers import ai, analytics, clients, energy_calculations, energy_schedule, health, reports, uploads, web

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

app.include_router(web.router)
app.include_router(health.router)
app.include_router(clients.router)
app.include_router(analytics.router)
app.include_router(reports.router)
app.include_router(ai.router)
app.include_router(energy_calculations.router)
app.include_router(energy_schedule.router)
app.include_router(uploads.router)

# Data storage
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# JWT Config
SECRET_KEY = "your-very-secret-key"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")

# Admin endpoints: list tables and view table rows (protected by JWT)
@app.get("/api/admin/tables")
async def list_tables(db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    inspector = inspect(db.bind)
    return {"tables": inspector.get_table_names()}


@app.get("/api/admin/table/{table_name}")
async def get_table_data(table_name: str, db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin), limit: int = 100, offset: int = 0):
    # Basic SQL injection protection
    if not table_name.isidentifier():
        raise HTTPException(status_code=400, detail="Invalid table name")
    sql = text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset")
    result = db.execute(sql, {"limit": limit, "offset": offset})
    columns = result.keys()
    raw_rows = result.fetchall()
    # Convert rows to JSON-serializable values (dates, datetimes)
    def serialize_value(v):
        from datetime import datetime, date
        if isinstance(v, datetime) or isinstance(v, date):
            return v.isoformat()
        try:
            # simple types will pass
            json.dumps(v)
            return v
        except Exception:
            return str(v)

    rows = []
    for row in raw_rows:
        d = {}
        for k, v in zip(columns, row):
            d[k] = serialize_value(v)
        rows.append(d)

    return {"columns": list(columns), "rows": rows}



# Demo admin credentials (replace with DB lookup and hashing in production)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # Change this in production!

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None


class WorkbookLoginRequest(BaseModel):
    email: str
    password: str
    portal: str


class WorkbookUserProfile(BaseModel):
    id: str
    tenant_id: str | None
    email: str
    full_name: str
    role_codes: List[str]


class WorkbookLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: WorkbookUserProfile


class ParsedSheetSummary(BaseModel):
    sheet_name: str
    sheet_type: str
    status: str
    row_count: int | None = None
    validation_summary: str | None = None


class WorkbookRowResponse(BaseModel):
    reading_date: str
    tneb_total: float
    iex_total: float
    solar_total: float
    tneb_balance: float
    banking_balance: float


class WorkbookUploadApiResponse(BaseModel):
    workbook_id: str
    file_name: str
    workbook_month: str | None
    status: str
    sheet_summaries: List[ParsedSheetSummary]
    calculation_summary: Dict[str, Any]
    preview_rows: List[WorkbookRowResponse]


class WorkbookListItemResponse(BaseModel):
    workbook_id: str
    file_name: str
    workbook_month: str | None
    status: str
    uploaded_at: str
    uploaded_by_user_id: str | None
    solar_working_rows: int


class WorkbookResultsApiResponse(BaseModel):
    workbook_id: str
    workbook_month: str | None
    status: str
    rows: List[WorkbookRowResponse]


WORKBOOK_DEMO_USERS = {
    "admin@demo.local": {
        "password": "Admin123!",
        "full_name": "Platform Admin",
        "role_codes": ["platform_admin", "tenant_admin"],
        "tenant_id": "demo-tenant",
    },
    "tenantadmin@demo.local": {
        "password": "Tenant123!",
        "full_name": "Tenant Admin",
        "role_codes": ["tenant_admin"],
        "tenant_id": "demo-tenant",
    },
    "client@demo.local": {
        "password": "Client123!",
        "full_name": "Client Viewer",
        "role_codes": ["client_viewer"],
        "tenant_id": "demo-tenant",
    },
}


def create_workbook_access_token(user_email: str) -> str:
    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_email, "exp": expires_at}, SECRET_KEY, algorithm=ALGORITHM)


def get_workbook_current_user(authorization: str | None = Header(default=None)) -> WorkbookUserProfile:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token.")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid bearer token.") from exc

    if not email or email not in WORKBOOK_DEMO_USERS:
        raise HTTPException(status_code=401, detail="Unknown workbook user.")

    user = WORKBOOK_DEMO_USERS[email]
    return WorkbookUserProfile(
        id=email,
        tenant_id=user["tenant_id"],
        email=email,
        full_name=user["full_name"],
        role_codes=user["role_codes"],
    )


def require_workbook_roles(*allowed_roles: str):
    def dependency(current_user: WorkbookUserProfile = Depends(get_workbook_current_user)) -> WorkbookUserProfile:
        if not set(current_user.role_codes).intersection(set(allowed_roles)):
            raise HTTPException(status_code=403, detail="User does not have the required role.")
        return current_user

    return dependency


def _normalize_workbook_month(file_name: str, result_rows: List[WorkbookRowResponse]) -> str | None:
    if result_rows:
        try:
            parsed = datetime.fromisoformat(result_rows[0].reading_date)
            return parsed.strftime("%Y-%m")
        except ValueError:
            pass

    match = re.search(r"([A-Za-z]{3})[' -]?(\d{2})", file_name)
    if not match:
        return None

    month_map = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    }
    month = month_map.get(match.group(1).lower())
    if not month:
        return None
    year = f"20{match.group(2)}"
    return f"{year}-{month}"


def _parse_date_value(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        trimmed = value.strip()
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y"):
            try:
                return datetime.strptime(trimmed, fmt).date()
            except ValueError:
                continue
    return None


def _to_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _parse_workbook_rows(file_name: str, content: bytes) -> tuple[List[ParsedSheetSummary], List[WorkbookRowResponse], str | None]:
    workbook = load_workbook(filename=BytesIO(content), data_only=True)
    sheet_summaries: List[ParsedSheetSummary] = []
    parsed_rows: List[WorkbookRowResponse] = []

    for sheet in workbook.worksheets:
        sheet_row_count = 0
        for row in sheet.iter_rows(values_only=True):
            if not row:
                continue
            reading_date = _parse_date_value(row[0])
            if reading_date is None:
                continue

            numeric_values = [_to_float(value) for value in row[1:] if _to_float(value) is not None]
            if len(numeric_values) < 4:
                continue

            sheet_row_count += 1
            tneb_total = numeric_values[0]
            iex_total = numeric_values[1]
            solar_total = numeric_values[2]
            tneb_balance = numeric_values[3]
            banking_balance = numeric_values[4] if len(numeric_values) > 4 else 0.0
            parsed_rows.append(
                WorkbookRowResponse(
                    reading_date=reading_date.isoformat(),
                    tneb_total=tneb_total,
                    iex_total=iex_total,
                    solar_total=solar_total,
                    tneb_balance=tneb_balance,
                    banking_balance=banking_balance,
                )
            )

        sheet_summaries.append(
            ParsedSheetSummary(
                sheet_name=sheet.title,
                sheet_type="worksheet",
                status="parsed" if sheet_row_count else "ignored",
                row_count=sheet_row_count,
                validation_summary=(
                    f"Parsed {sheet_row_count} candidate rows." if sheet_row_count else "No date-plus-numeric rows detected."
                ),
            )
        )

    parsed_rows.sort(key=lambda item: item.reading_date)

    if not parsed_rows:
        today = datetime.utcnow().date()
        parsed_rows = [
            WorkbookRowResponse(
                reading_date=today.isoformat(),
                tneb_total=0.0,
                iex_total=0.0,
                solar_total=0.0,
                tneb_balance=0.0,
                banking_balance=0.0,
            )
        ]

    workbook_month = _normalize_workbook_month(file_name, parsed_rows)
    return sheet_summaries, parsed_rows, workbook_month

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_admin(username: str, password: str):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return {"username": username}
    return None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    if token_data.username != ADMIN_USERNAME:
        raise credentials_exception
    return {"username": token_data.username}

# Admin login endpoint
@app.post("/api/admin/login", response_model=Token)
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_admin(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoint to verify JWT auth
@app.get("/api/admin/me")
async def read_admin_me(current_admin: dict = Depends(get_current_admin)):
    return {"username": current_admin["username"]}


@app.post("/api/v1/auth/login", response_model=WorkbookLoginResponse)
async def workbook_login(payload: WorkbookLoginRequest):
    user = WORKBOOK_DEMO_USERS.get(payload.email)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    profile = WorkbookUserProfile(
        id=payload.email,
        tenant_id=user["tenant_id"],
        email=payload.email,
        full_name=user["full_name"],
        role_codes=user["role_codes"],
    )
    access_token = create_workbook_access_token(payload.email)
    return WorkbookLoginResponse(access_token=access_token, token_type="bearer", user=profile)


@app.get("/api/v1/workbooks", response_model=List[WorkbookListItemResponse])
async def read_workbooks(
    db: Session = Depends(get_db),
    current_user: WorkbookUserProfile = Depends(
        require_workbook_roles("platform_admin", "tenant_admin", "client_viewer")
    ),
):
    uploads = db.query(WorkbookUploadRecord).order_by(WorkbookUploadRecord.uploaded_at.desc()).all()
    results: List[WorkbookListItemResponse] = []
    for upload in uploads:
        row_count = db.query(WorkbookResultRow).filter(WorkbookResultRow.workbook_id == upload.id).count()
        results.append(
            WorkbookListItemResponse(
                workbook_id=upload.id,
                file_name=upload.file_name,
                workbook_month=upload.workbook_month,
                status=upload.status,
                uploaded_at=upload.uploaded_at.isoformat() if upload.uploaded_at else datetime.utcnow().isoformat(),
                uploaded_by_user_id=upload.uploaded_by,
                solar_working_rows=row_count,
            )
        )
    return results


@app.post("/api/v1/workbooks/upload", response_model=WorkbookUploadApiResponse)
async def upload_workbook_v1(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: WorkbookUserProfile = Depends(
        require_workbook_roles("platform_admin", "tenant_admin", "client_viewer")
    ),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required.")
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx workbooks are supported.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    sheet_summaries, parsed_rows, workbook_month = _parse_workbook_rows(file.filename, content)
    workbook_id = str(uuid4())
    workbook_dir = OUTPUT_DIR / "workbook_uploads"
    workbook_dir.mkdir(parents=True, exist_ok=True)
    stored_path = workbook_dir / f"{workbook_id}.xlsx"
    stored_path.write_bytes(content)

    upload = WorkbookUploadRecord(
        id=workbook_id,
        file_name=file.filename,
        workbook_month=workbook_month,
        status="calculated",
        uploaded_by=current_user.id,
        stored_file_path=str(stored_path),
    )
    db.add(upload)
    db.flush()

    for row in parsed_rows:
        db.add(
            WorkbookResultRow(
                workbook_id=workbook_id,
                reading_date=datetime.fromisoformat(row.reading_date).date(),
                tneb_total=row.tneb_total,
                iex_total=row.iex_total,
                solar_total=row.solar_total,
                tneb_balance=row.tneb_balance,
                banking_balance=row.banking_balance,
            )
        )

    db.commit()

    return WorkbookUploadApiResponse(
        workbook_id=workbook_id,
        file_name=file.filename,
        workbook_month=workbook_month,
        status="calculated",
        sheet_summaries=sheet_summaries,
        calculation_summary={"row_count": len(parsed_rows)},
        preview_rows=parsed_rows[:10],
    )


@app.get("/api/v1/workbooks/{workbook_id}/solar-working", response_model=WorkbookResultsApiResponse)
async def read_workbook_results(
    workbook_id: str,
    db: Session = Depends(get_db),
    current_user: WorkbookUserProfile = Depends(
        require_workbook_roles("platform_admin", "tenant_admin", "client_viewer")
    ),
):
    upload = db.query(WorkbookUploadRecord).filter(WorkbookUploadRecord.id == workbook_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Workbook not found.")

    rows = (
        db.query(WorkbookResultRow)
        .filter(WorkbookResultRow.workbook_id == workbook_id)
        .order_by(WorkbookResultRow.reading_date.asc())
        .all()
    )
    return WorkbookResultsApiResponse(
        workbook_id=upload.id,
        workbook_month=upload.workbook_month,
        status=upload.status,
        rows=[
            WorkbookRowResponse(
                reading_date=row.reading_date.isoformat(),
                tneb_total=row.tneb_total,
                iex_total=row.iex_total,
                solar_total=row.solar_total,
                tneb_balance=row.tneb_balance,
                banking_balance=row.banking_balance,
            )
            for row in rows
        ],
    )

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database when app starts"""
    print("🗄️  Initializing database...")
    init_db()
    print("✅ Database ready")
    
    if os.getenv("AUTO_LOAD_MOCK_DATA", "false").lower() == "true":
        try:
            from database.config import SessionLocal
            from database.services import get_all_clients
            
            db = SessionLocal()
            try:
                clients = get_all_clients(db)
                if len(clients) == 0:
                    print("📊 Database is empty, loading mock data...")
                    import subprocess
                    subprocess.run([sys.executable, "scripts/data_generation/generate_mock_reports.py"], check=False)
                    subprocess.run([sys.executable, "scripts/ingestion/upload_mock_reports.py"], check=False)
                    subprocess.run([sys.executable, "scripts/energy_schedule/rebuild_energy_schedules.py"], check=False)
                    print("✅ Mock data loaded")
                else:
                    print(f"✅ Database has {len(clients)} clients already")
            finally:
                db.close()
        except Exception as e:
            print(f"⚠️  Mock data load failed: {e}")
            print("   You can upload files manually via the UI")
    else:
        print("ℹ️  AUTO_LOAD_MOCK_DATA is disabled")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
