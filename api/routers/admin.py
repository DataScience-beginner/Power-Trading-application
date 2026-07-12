"""Database inspection routes protected by the enterprise platform-admin identity."""

import json
from datetime import date, datetime
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from api.security.chat_auth import require_admin
from database.chatbot_models import AppUser
from database.config import get_db


router = APIRouter(tags=["admin"])

@router.get(
    "/api/admin/tables",
    response_model=dict[str, list[str]],
    summary="List database tables",
    description="Protected admin endpoint that lists database table names.",
)
async def list_tables(
    db: Session = Depends(get_db),
    _admin: AppUser = Depends(require_admin),
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
    _admin: AppUser = Depends(require_admin),
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
    "/api/admin/reset-database",
    response_model=dict[str, object],
    summary="Reset database",
    description="Destructive admin endpoint that deletes all demo/client trading data and calculations.",
)
async def reset_database(
    db: Session = Depends(get_db),
    _admin: AppUser = Depends(require_admin),
) -> dict[str, object]:
    """Reset database tables in dependency-safe order."""
    if os.getenv("ENABLE_DATABASE_RESET", "false").lower() != "true":
        raise HTTPException(status_code=404, detail="Database reset is disabled")
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
