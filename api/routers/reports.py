"""Report export routes for PDF and Excel downloads."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from api.report_generator import (
    generate_daily_trading_excel,
    generate_daily_trading_pdf,
    generate_energy_schedule_pdf,
)
from database.config import get_db
from database.models import DailyFile, EnergyScheduleDay, EnergyScheduleMonth, Portfolio, Transaction


router = APIRouter(tags=["reports"])


@router.get(
    "/api/reports/daily-trading/pdf",
    summary="Export daily trading PDF",
    description="Generates a PDF report for daily trading transactions filtered by date and/or portfolio.",
)
async def download_daily_trading_pdf(
    date: str = None,
    portfolio_code: str = None,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Generate and stream a daily trading PDF report."""
    try:
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
                "amount": t.amount,
            }
            for t in transactions
        ]

        pdf_buffer = generate_daily_trading_pdf(trans_data, date or datetime.now().strftime("%Y-%m-%d"))

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=Daily_Trading_Report_{date or 'latest'}.pdf"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}") from e


@router.get(
    "/api/reports/daily-trading/excel",
    summary="Export daily trading Excel",
    description="Generates an Excel report for daily trading transactions filtered by date and/or portfolio.",
)
async def download_daily_trading_excel(
    date: str = None,
    portfolio_code: str = None,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Generate and stream a daily trading Excel report."""
    try:
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
                "amount": t.amount,
            }
            for t in transactions
        ]

        excel_buffer = generate_daily_trading_excel(trans_data, date or datetime.now().strftime("%Y-%m-%d"))

        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=Daily_Trading_Report_{date or 'latest'}.xlsx"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Excel: {str(e)}") from e


@router.get(
    "/api/reports/energy-schedule/pdf",
    summary="Export energy schedule PDF",
    description="Generates a PDF report for energy schedule analysis filtered by portfolio and/or date range.",
)
async def download_energy_schedule_pdf(
    portfolio_id: int = None,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Generate and stream an energy schedule PDF report."""
    try:
        query = db.query(EnergyScheduleDay)

        if portfolio_id:
            query = query.join(EnergyScheduleMonth).filter(EnergyScheduleMonth.portfolio_id == portfolio_id)

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
                "total_cost": day.total_cost or 0,
            }
            for day in days
        ]

        pdf_buffer = generate_energy_schedule_pdf(days_data)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Energy_Schedule_Report.pdf"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}") from e

