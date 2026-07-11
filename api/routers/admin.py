"""Admin authentication, database inspection, and reset routes."""

import json
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from database.config import get_db


router = APIRouter(tags=["admin"])

SECRET_KEY = "your-very-secret-key"  # Preserve current behavior; move to env later.
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # Preserve current behavior; replace with DB-backed auth later.


class Token(BaseModel):
    """Admin access token response."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Decoded admin token payload."""

    username: str | None = None


def authenticate_admin(username: str, password: str) -> dict[str, str] | None:
    """Authenticate demo admin credentials."""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return {"username": username}
    return None


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token for admin routes."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_admin(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
    """Resolve current admin from JWT bearer token."""
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
    except JWTError as exc:
        raise credentials_exception from exc
    if token_data.username != ADMIN_USERNAME:
        raise credentials_exception
    return {"username": token_data.username}


@router.get(
    "/api/admin/tables",
    response_model=dict[str, list[str]],
    summary="List database tables",
    description="Protected admin endpoint that lists database table names.",
)
async def list_tables(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
) -> dict[str, list[str]]:
    """Return database table names for the authenticated admin."""
    inspector = inspect(db.bind)
    return {"tables": inspector.get_table_names()}


@router.get(
    "/api/admin/table/{table_name}",
    response_model=dict[str, object],
    summary="Read database table rows",
    description="Protected admin endpoint that returns paginated rows for a selected table.",
)
async def get_table_data(
    table_name: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
    limit: int = 100,
    offset: int = 0,
) -> dict[str, object]:
    """Return selected table rows with basic table-name validation."""
    if not table_name.isidentifier():
        raise HTTPException(status_code=400, detail="Invalid table name")

    sql = text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset")
    result = db.execute(sql, {"limit": limit, "offset": offset})
    columns = result.keys()
    raw_rows = result.fetchall()

    def serialize_value(value):
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        try:
            json.dumps(value)
            return value
        except Exception:
            return str(value)

    rows = []
    for row in raw_rows:
        rows.append({key: serialize_value(value) for key, value in zip(columns, row)})

    return {"columns": list(columns), "rows": rows}


@router.post(
    "/api/admin/login",
    response_model=Token,
    summary="Admin login",
    description="Authenticates admin credentials and returns a bearer token for protected admin endpoints.",
)
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Authenticate admin and return bearer token."""
    user = authenticate_admin(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/api/admin/me",
    response_model=dict[str, str],
    summary="Get current admin",
    description="Verifies the current admin bearer token and returns the username.",
)
async def read_admin_me(current_admin: dict = Depends(get_current_admin)) -> dict[str, str]:
    """Return current admin identity."""
    return {"username": current_admin["username"]}


@router.post(
    "/api/admin/reset-database",
    response_model=dict[str, object],
    summary="Reset database",
    description="Destructive admin endpoint that deletes all demo/client trading data and calculations.",
)
async def reset_database(db: Session = Depends(get_db)) -> dict[str, object]:
    """Reset database tables in dependency-safe order."""
    from database.models import (
        Client,
        DailyFile,
        EnergyScheduleDay,
        EnergyScheduleMonth,
        MonthlyCalculation,
        Portfolio,
        Transaction,
    )

    try:
        clients_count = db.query(Client).count()
        portfolios_count = db.query(Portfolio).count()
        files_count = db.query(DailyFile).count()
        transactions_count = db.query(Transaction).count()

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
                "transactions": transactions_count,
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database reset failed: {str(e)}") from e

