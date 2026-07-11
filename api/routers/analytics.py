"""Analytics routes for dashboards, agents, and chatbot explanations."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import DailyFile, Portfolio, Transaction
from api.security.chat_auth import get_current_user
from database.chatbot_models import AppUser, UserPortfolioAccess


router = APIRouter(tags=["analytics"])


class AnalyticsSummaryMetrics(BaseModel):
    """Dashboard-level analytics summary metrics."""

    dor_files: int
    sch_files: int
    total_files: int
    total_transactions: int
    net_amount: float
    buy_transactions: int
    sell_transactions: int
    scheduling_transactions: int


class HourlyDistributionItem(BaseModel):
    """Hourly aggregated quantity metric."""

    hour: int
    avg_quantity: float


class AnalyticsSummaryResponse(BaseModel):
    """Response for the dashboard analytics summary."""

    success: bool
    summary: AnalyticsSummaryMetrics
    hourly_distribution: list[HourlyDistributionItem]


class DorVsSchComparison(BaseModel):
    """Hourly DOR-vs-SCH comparison arrays."""

    hours: list[str]
    dor_values: list[float]
    sch_values: list[float]


class DorVsSchResponse(BaseModel):
    """Response for DOR-vs-SCH comparison on a trading date."""

    success: bool
    trading_date: str
    dor_files: int
    sch_files: int
    comparison: DorVsSchComparison


@router.get(
    "/api/analytics/summary",
    response_model=AnalyticsSummaryResponse,
    summary="Get analytics summary",
    description="Returns dashboard summary metrics for DOR/SCH files and transaction activity.",
)
async def get_analytics_summary(
    portfolio_code: str = None,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db),
    user: AppUser = Depends(get_current_user),
) -> AnalyticsSummaryResponse:
    """Return dashboard analytics summary metrics with optional portfolio/date filters."""
    try:
        file_query = db.query(DailyFile).join(Portfolio)
        permitted_portfolios: set[int] = set()
        if user.role != "platform_admin":
            file_query = file_query.filter(Portfolio.client_id == user.client_id)
            permitted_portfolios = {
                item.portfolio_id
                for item in db.query(UserPortfolioAccess).filter(UserPortfolioAccess.user_id == user.id).all()
            }
            if permitted_portfolios:
                file_query = file_query.filter(Portfolio.id.in_(permitted_portfolios))

        if portfolio_code:
            file_query = file_query.filter(Portfolio.portfolio_code == portfolio_code)

        if start_date:
            start = datetime.fromisoformat(start_date).date()
            file_query = file_query.filter(DailyFile.trading_date >= start)

        if end_date:
            end = datetime.fromisoformat(end_date).date()
            file_query = file_query.filter(DailyFile.trading_date <= end)

        files = file_query.all()

        dor_count = sum(1 for f in files if f.report_type.startswith("DOR"))
        sch_count = sum(1 for f in files if f.report_type.startswith("SCH"))

        txn_query = db.query(Transaction).join(DailyFile).join(Portfolio)
        if user.role != "platform_admin":
            txn_query = txn_query.filter(Portfolio.client_id == user.client_id)
            if permitted_portfolios:
                txn_query = txn_query.filter(Portfolio.id.in_(permitted_portfolios))

        if portfolio_code:
            txn_query = txn_query.filter(Portfolio.portfolio_code == portfolio_code)

        if start_date:
            txn_query = txn_query.filter(Transaction.date >= datetime.fromisoformat(start_date).date())

        if end_date:
            txn_query = txn_query.filter(Transaction.date <= datetime.fromisoformat(end_date).date())

        total_transactions = txn_query.count()

        total_amount = db.query(func.sum(Transaction.amount)).join(DailyFile).join(Portfolio)
        if user.role != "platform_admin":
            total_amount = total_amount.filter(Portfolio.client_id == user.client_id)
            if permitted_portfolios:
                total_amount = total_amount.filter(Portfolio.id.in_(permitted_portfolios))
        if portfolio_code:
            total_amount = total_amount.filter(Portfolio.portfolio_code == portfolio_code)
        if start_date:
            total_amount = total_amount.filter(Transaction.date >= datetime.fromisoformat(start_date).date())
        if end_date:
            total_amount = total_amount.filter(Transaction.date <= datetime.fromisoformat(end_date).date())

        net_amount = total_amount.scalar() or 0

        hourly_data = []
        buy_count = txn_query.filter(Transaction.transaction_type == "buy").count()
        sell_count = txn_query.filter(Transaction.transaction_type == "sell").count()
        scheduling_count = txn_query.filter(Transaction.transaction_type == "scheduling").count()

        return AnalyticsSummaryResponse(
            success=True,
            summary=AnalyticsSummaryMetrics(
                dor_files=dor_count,
                sch_files=sch_count,
                total_files=len(files),
                total_transactions=total_transactions,
                net_amount=float(net_amount),
                buy_transactions=buy_count,
                sell_transactions=sell_count,
                scheduling_transactions=scheduling_count,
            ),
            hourly_distribution=[
                HourlyDistributionItem(
                    hour=int(h[0]) if h[0] else 0,
                    avg_quantity=float(h[1]) if h[1] else 0,
                )
                for h in hourly_data
            ]
            if hourly_data
            else [],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}") from e


@router.get(
    "/api/analytics/dor-vs-sch",
    response_model=DorVsSchResponse,
    summary="Compare DOR and SCH",
    description="Compares DOR and SCH hourly quantities for a portfolio/date to explain schedule variance.",
)
async def get_dor_vs_sch_comparison(
    portfolio_code: str = None,
    trading_date: str = None,
    db: Session = Depends(get_db),
    user: AppUser = Depends(get_current_user),
) -> DorVsSchResponse:
    """Return hourly DOR-vs-SCH comparison for a trading date."""
    try:
        if not trading_date:
            raise HTTPException(status_code=400, detail="trading_date parameter required")

        date_obj = datetime.fromisoformat(trading_date).date()

        dor_query = db.query(DailyFile).join(Portfolio).filter(
            DailyFile.trading_date == date_obj,
            DailyFile.report_type.like("DOR%"),
        )
        if user.role != "platform_admin":
            dor_query = dor_query.filter(Portfolio.client_id == user.client_id)
        if portfolio_code:
            dor_query = dor_query.filter(Portfolio.portfolio_code == portfolio_code)

        sch_query = db.query(DailyFile).join(Portfolio).filter(
            DailyFile.trading_date == date_obj,
            DailyFile.report_type.like("SCH%"),
        )
        if user.role != "platform_admin":
            sch_query = sch_query.filter(Portfolio.client_id == user.client_id)
        if portfolio_code:
            sch_query = sch_query.filter(Portfolio.portfolio_code == portfolio_code)

        dor_files = dor_query.all()
        sch_files = sch_query.all()

        dor_hourly: dict[str, list[float]] = {}
        for file in dor_files:
            transactions = db.query(Transaction).filter(Transaction.daily_file_id == file.id).all()
            for txn in transactions:
                hour = txn.time_slot.split(" - ")[0]
                dor_hourly.setdefault(hour, []).append(txn.quantity_mw or 0)

        sch_hourly: dict[str, list[float]] = {}
        for file in sch_files:
            transactions = db.query(Transaction).filter(Transaction.daily_file_id == file.id).all()
            for txn in transactions:
                hour = txn.time_slot.split(" - ")[0]
                sch_hourly.setdefault(hour, []).append(txn.quantity_mw or txn.total_quantity_mw or 0)

        dor_data = {hour: sum(vals) / len(vals) for hour, vals in dor_hourly.items()}
        sch_data = {hour: sum(vals) / len(vals) for hour, vals in sch_hourly.items()}
        hours = sorted(set(list(dor_data.keys()) + list(sch_data.keys())))

        return DorVsSchResponse(
            success=True,
            trading_date=trading_date,
            dor_files=len(dor_files),
            sch_files=len(sch_files),
            comparison=DorVsSchComparison(
                hours=hours,
                dor_values=[dor_data.get(h, 0) for h in hours],
                sch_values=[sch_data.get(h, 0) for h in hours],
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching DOR vs SCH comparison: {str(e)}") from e
