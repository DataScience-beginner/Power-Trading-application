"""Client, portfolio, and transaction routes."""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import services as db_services
from database.config import get_db


router = APIRouter(tags=["clients"])


class TransactionUpdateResponse(BaseModel):
    """Response returned after an admin transaction override."""

    success: bool = Field(..., description="Whether the transaction was updated.")
    message: str = Field(..., description="Human-readable update result.")
    transaction_id: int = Field(..., description="Updated transaction identifier.")
    updated_fields: list[str] = Field(..., description="Fields updated by the request.")


class PortfolioDailyFileItem(BaseModel):
    """Daily file summary for a portfolio/date."""

    id: int
    report_type: str | None
    main_category: str | None
    sub_category: str | None
    original_filename: str | None
    uploaded_at: str
    transaction_count: int


class PortfolioDailyFilesResponse(BaseModel):
    """Response containing daily files for a portfolio."""

    success: bool
    portfolio: str
    trading_date: str | None = None
    file_count: int | None = None
    max_files: int | None = None
    files: list[PortfolioDailyFileItem] | None = None
    message: str | None = None


class FileTransactionItem(BaseModel):
    """Transaction row belonging to a parsed daily file."""

    id: int
    date: str
    time_slot: str | None
    transaction_type: str
    quantity_mw: float | None
    rate_per_mwh: float | None
    amount: float | None
    solar_quantity_mw: float | None
    non_solar_quantity_mw: float | None
    hydro_quantity_mw: float | None
    total_quantity_mw: float | None
    regional_injection_mw: float | None
    regional_drawal_mw: float | None
    regional_net_mw: float | None
    interface_injection_mw: float | None
    interface_drawal_mw: float | None
    interface_net_mw: float | None
    total_losses_mw: float | None


class FileTransactionsResponse(BaseModel):
    """Response containing all transactions for a daily file."""

    success: bool
    file_id: int
    transaction_count: int
    transactions: list[FileTransactionItem]


class ClientSummaryItem(BaseModel):
    """Client summary used by dashboards and assistant workflows."""

    id: int
    entity_id: str
    entity_name: str
    portfolio_count: int


class ClientsResponse(BaseModel):
    """Response containing all clients available in the platform."""

    success: bool
    count: int
    clients: list[ClientSummaryItem]


class TransactionListItem(BaseModel):
    """Flattened transaction item for dashboard and assistant analysis."""

    id: int
    file_id: int
    date: str
    time_slot: str | None
    transaction_type: str
    type: str
    report_type: str
    portfolio_code: str
    entity_name: str
    entity_id: str
    quantity: float | None
    quantity_mw: float | None
    rate: float | None
    rate_per_mwh: float | None
    amount: float | None
    solar_quantity_mw: float | None
    non_solar_quantity_mw: float | None
    total_quantity_mw: float | None


class TransactionsListResponse(BaseModel):
    """Response containing filtered transactions."""

    success: bool
    total_count: int
    count: int
    transactions: list[TransactionListItem]


@router.put(
    "/api/transactions/{transaction_id}",
    response_model=TransactionUpdateResponse,
    summary="Update transaction",
    description="Admin override endpoint used to manually correct parsed transaction values.",
)
async def update_transaction(
    transaction_id: int,
    updates: dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
) -> TransactionUpdateResponse:
    """Update selected fields on a transaction while preserving the existing request shape."""
    try:
        updated_txn = db_services.update_transaction(db, transaction_id, updates)

        if not updated_txn:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return TransactionUpdateResponse(
            success=True,
            message="Transaction updated successfully",
            transaction_id=transaction_id,
            updated_fields=list(updates.keys()),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating transaction: {str(e)}") from e


@router.get(
    "/api/portfolios/{portfolio_code}/daily-files",
    response_model=PortfolioDailyFilesResponse,
    summary="Get portfolio daily files",
    description="Returns uploaded daily files for a portfolio, optionally filtered by trading date.",
)
async def get_portfolio_daily_files(
    portfolio_code: str,
    trading_date: Optional[str] = None,
    db: Session = Depends(get_db),
) -> PortfolioDailyFilesResponse:
    """Return daily files for a portfolio/date to support dashboard completeness checks."""
    try:
        portfolio = db_services.get_portfolio_by_code(db, portfolio_code)

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        if trading_date:
            date_obj = datetime.fromisoformat(trading_date).date()
            files = db_services.get_daily_files_by_date(db, portfolio.id, date_obj)

            return PortfolioDailyFilesResponse(
                success=True,
                portfolio=portfolio_code,
                trading_date=trading_date,
                file_count=len(files),
                max_files=6,
                files=[
                    PortfolioDailyFileItem(
                        id=f.id,
                        report_type=f.report_type,
                        main_category=f.main_category,
                        sub_category=f.sub_category,
                        original_filename=f.original_filename,
                        uploaded_at=f.uploaded_at.isoformat(),
                        transaction_count=len(f.transactions),
                    )
                    for f in files
                ],
            )

        return PortfolioDailyFilesResponse(
            success=True,
            portfolio=portfolio_code,
            message="Provide trading_date parameter to see files for a specific date",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching files: {str(e)}") from e


@router.get(
    "/api/files/{file_id}/transactions",
    response_model=FileTransactionsResponse,
    summary="Get file transactions",
    description="Returns all parsed transaction rows for a specific daily file.",
)
async def get_file_transactions(
    file_id: int,
    db: Session = Depends(get_db),
) -> FileTransactionsResponse:
    """Return all transactions for a parsed daily file."""
    try:
        transactions = db_services.get_transactions_by_file(db, file_id)

        return FileTransactionsResponse(
            success=True,
            file_id=file_id,
            transaction_count=len(transactions),
            transactions=[
                FileTransactionItem(
                    id=txn.id,
                    date=txn.date.isoformat(),
                    time_slot=txn.time_slot,
                    transaction_type=txn.transaction_type,
                    quantity_mw=txn.quantity_mw,
                    rate_per_mwh=txn.rate_per_mwh,
                    amount=txn.amount,
                    solar_quantity_mw=txn.solar_quantity_mw,
                    non_solar_quantity_mw=txn.non_solar_quantity_mw,
                    hydro_quantity_mw=txn.hydro_quantity_mw,
                    total_quantity_mw=txn.total_quantity_mw,
                    regional_injection_mw=txn.regional_injection_mw,
                    regional_drawal_mw=txn.regional_drawal_mw,
                    regional_net_mw=txn.regional_net_mw,
                    interface_injection_mw=txn.interface_injection_mw,
                    interface_drawal_mw=txn.interface_drawal_mw,
                    interface_net_mw=txn.interface_net_mw,
                    total_losses_mw=txn.total_losses_mw,
                )
                for txn in transactions
            ],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}") from e


@router.get(
    "/api/clients",
    response_model=ClientsResponse,
    summary="List clients",
    description="Returns clients available for dashboard, analytics, and assistant workflows.",
)
async def get_clients(db: Session = Depends(get_db)) -> ClientsResponse:
    """Return all clients with portfolio counts."""
    try:
        clients = db_services.get_all_clients(db)
        return ClientsResponse(
            success=True,
            count=len(clients),
            clients=[
                ClientSummaryItem(
                    id=c.id,
                    entity_id=c.entity_id,
                    entity_name=c.entity_name,
                    portfolio_count=len(c.portfolios),
                )
                for c in clients
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching clients: {str(e)}") from e


@router.get(
    "/api/transactions/all",
    response_model=TransactionsListResponse,
    summary="List transactions",
    description="Returns filtered transaction rows for dashboard and assistant analysis.",
)
async def get_all_transactions(
    portfolio_code: str = None,
    start_date: str = None,
    end_date: str = None,
    report_type: str = None,
    db: Session = Depends(get_db),
) -> TransactionsListResponse:
    """Return filtered transactions with a hard limit for dashboard performance."""
    try:
        from database.models import DailyFile, Portfolio, Transaction

        query = db.query(Transaction).join(DailyFile).join(Portfolio)

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

        total_count = query.count()
        transactions = query.order_by(Transaction.date.desc(), Transaction.time_slot).limit(10000).all()

        return TransactionsListResponse(
            success=True,
            total_count=total_count,
            count=len(transactions),
            transactions=[
                TransactionListItem(
                    id=t.id,
                    file_id=t.daily_file_id,
                    date=t.date.isoformat(),
                    time_slot=t.time_slot,
                    transaction_type=t.transaction_type,
                    type=(
                        "BUY"
                        if "buy" in t.transaction_type.lower()
                        else "SELL"
                        if "sell" in t.transaction_type.lower()
                        else "SCHEDULE"
                    ),
                    report_type=t.daily_file.report_type,
                    portfolio_code=t.daily_file.portfolio.portfolio_code,
                    entity_name=t.daily_file.portfolio.client.entity_name,
                    entity_id=t.daily_file.portfolio.client.entity_id,
                    quantity=t.quantity_mw,
                    quantity_mw=t.quantity_mw,
                    rate=t.rate_per_mwh,
                    rate_per_mwh=t.rate_per_mwh,
                    amount=t.amount,
                    solar_quantity_mw=t.solar_quantity_mw,
                    non_solar_quantity_mw=t.non_solar_quantity_mw,
                    total_quantity_mw=t.total_quantity_mw,
                )
                for t in transactions
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}") from e

