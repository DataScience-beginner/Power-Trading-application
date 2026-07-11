"""Core energy schedule routes."""

from datetime import date as dt_date
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from database.config import get_db
from database.energy_schedule_crud import get_all_daily_entries, get_all_month_sheets
from database.energy_schedule_service import calculator
from database.models import EnergyScheduleDay, EnergyScheduleMonth


router = APIRouter(tags=["energy-schedule"])


@router.get(
    "/api/energy-schedule/days",
    response_model=dict[str, Any],
    summary="List energy schedule days",
    description="Returns daily energy schedule records with completeness flags, CTU losses, savings, costs, and consumption.",
)
async def get_energy_schedule_days(
    portfolio_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    complete_only: bool = False,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return energy schedule day records with calculations."""
    try:
        query = db.query(EnergyScheduleDay).join(EnergyScheduleMonth)

        if portfolio_id:
            query = query.filter(EnergyScheduleMonth.portfolio_id == portfolio_id)
        if complete_only:
            query = query.filter(EnergyScheduleDay.is_complete == 1)
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(EnergyScheduleDay.trading_date >= start)
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(EnergyScheduleDay.trading_date <= end)

        days = query.order_by(EnergyScheduleDay.trading_date).all()

        result = [
            {
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
                "total_consumption_mwh": (
                    round(day.total_consumption_after_losses_mwh, 2)
                    if day.total_consumption_after_losses_mwh
                    else 0
                ),
            }
            for day in days
        ]

        return {"success": True, "count": len(result), "days": result}

    except Exception as e:
        import traceback

        print(traceback.format_exc())
        return {"success": False, "error": str(e)}


@router.post(
    "/api/calculate/energy-schedule",
    response_model=dict[str, Any],
    summary="Calculate energy schedule",
    description="Runs the energy schedule calculator for a requested calculation date.",
)
async def calculate_energy_schedule(
    request_data: dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Calculate energy schedule using the existing calculator service."""
    try:
        calculation_date_str = request_data.get("calculation_date")
        print(f"🔍 Calculate request - calculation_date: {calculation_date_str}")

        if calculation_date_str:
            try:
                calc_date = datetime.fromisoformat(calculation_date_str).date()
            except Exception:
                calc_date = datetime.strptime(calculation_date_str.split("T")[0], "%Y-%m-%d").date()
        else:
            calc_date = dt_date.today()

        print(f"📅 Using calculation date: {calc_date}")
        return calculator.calculate_energy_schedule(calc_date, db)

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"❌ Error in calculate_energy_schedule: {error_details}")

        return {
            "success": False,
            "message": f"Calculation failed: {str(e)}",
            "error": str(e),
        }


@router.get(
    "/api/energy-schedule/status",
    response_model=dict[str, Any],
    summary="Get energy schedule status",
    description="Returns recent energy schedule calculation status records.",
)
async def get_energy_schedule_status(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return recent energy schedule calculation status."""
    try:
        query = db.query(EnergyScheduleDay).order_by(EnergyScheduleDay.trading_date.desc()).limit(30)
        schedules_objs = query.all()

        schedules = [
            {
                "id": s.id,
                "month_sheet_id": s.month_sheet_id,
                "trading_date": str(s.trading_date),
                "scheduled_mwh": float(s.gdam_scheduled_quantity_mwh or 0)
                + float(s.dam_scheduled_quantity_mwh or 0)
                + float(s.rtm_scheduled_quantity_mwh or 0),
                "consumption_after_losses_mwh": float(s.sch_consumption_after_losses_mwh or 0),
                "gdam_cost": float(s.gdam_cost) if s.gdam_cost else 0.0,
                "dam_cost": float(s.dam_cost) if s.dam_cost else 0.0,
                "rtm_cost": float(s.rtm_cost) if s.rtm_cost else 0.0,
                "ctu_loss_percentage": float(s.ctu_loss_percentage) if s.ctu_loss_percentage else 0.0,
            }
            for s in schedules_objs
        ]

        return {"success": True, "count": len(schedules), "schedules": schedules}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching energy schedule status: {str(e)}") from e


@router.get(
    "/api/energy-schedule/months",
    response_model=list[dict[str, Any]],
    summary="List energy schedule months",
    description="Returns month sheets with summary metrics for the Energy Schedule frontend.",
)
async def get_energy_schedule_months(
    portfolio_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return all energy schedule month sheets, optionally filtered by portfolio."""
    try:
        month_sheets = get_all_month_sheets(db, portfolio_id)

        result = []
        for sheet in month_sheets:
            total_nldc = 0.0
            total_ctu = 0.0
            for day in sheet.daily_entries:
                total_nldc += (day.gdam_nldc_fee or 0) + (day.dam_nldc_fee or 0) + (day.rtm_nldc_fee or 0)
                total_ctu += (day.gdam_ctu_charges or 0) + (day.dam_ctu_charges or 0) + (day.rtm_ctu_charges or 0)

            result.append(
                {
                    "id": sheet.id,
                    "portfolio_id": sheet.portfolio_id,
                    "year": sheet.year,
                    "month": sheet.month,
                    "month_name": sheet.month_name,
                    "total_scheduled_mwh": sheet.total_scheduled_mwh,
                    "total_consumption_after_losses_mwh": sheet.total_consumption_after_losses_mwh,
                    "total_energy_savings": sheet.total_energy_savings_mwh,
                    "total_gdam_cost": sheet.total_gdam_cost,
                    "total_dam_cost": sheet.total_dam_cost,
                    "total_rtm_cost": sheet.total_rtm_cost,
                    "total_nldc_fees": total_nldc,
                    "total_ctu_charges": total_ctu,
                    "total_cost": sheet.total_gdam_cost + sheet.total_dam_cost + sheet.total_rtm_cost,
                    "average_ctu_losses": sheet.average_ctu_losses_percent,
                    "total_days_completed": sheet.days_completed,
                    "is_complete": sheet.is_complete,
                    "created_at": sheet.created_at.isoformat() if sheet.created_at else None,
                    "updated_at": sheet.updated_at.isoformat() if sheet.updated_at else None,
                }
            )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching month sheets: {str(e)}") from e


@router.get(
    "/api/energy-schedule/days",
    response_model=dict[str, Any],
    summary="List energy schedule days by date",
    description="Legacy duplicate route retained in the same order for compatibility; current FastAPI behavior uses the first matching route.",
)
async def get_energy_schedule_days_by_date(
    portfolio_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return daily entries by date range. Kept for compatibility with current route registration order."""
    try:
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

        result = [
            {
                "id": entry.id,
                "trading_date": entry.trading_date.isoformat(),
                "portfolio_id": entry.month_sheet.portfolio_id,
                "total_scheduled_mwh": float(entry.total_scheduled_mwh or 0),
                "total_consumption_after_losses_mwh": float(entry.total_consumption_after_losses_mwh or 0),
                "ctu_losses_percent": float(entry.ctu_losses_percent or 0),
                "ctu_losses_mwh": float(entry.ctu_losses_mwh or 0),
                "gdam_cost": float(entry.gdam_cost or 0),
                "dam_cost": float(entry.dam_cost or 0),
                "rtm_cost": float(entry.rtm_cost or 0),
                "total_cost": float(entry.total_cost or 0),
                "energy_savings_mwh": float(entry.energy_savings_mwh or 0),
                "total_nldc_fee": float(entry.total_nldc_fee or 0),
                "total_ctu_charges": float(entry.total_ctu_charges or 0),
                "has_gdam_data": bool(entry.has_gdam_data),
                "has_dam_data": bool(entry.has_dam_data),
                "has_rtm_data": bool(entry.has_rtm_data),
                "has_sch_data": bool(entry.has_sch_data),
                "is_complete": bool(entry.is_complete),
                "calculated_at": entry.calculated_at.isoformat() if entry.calculated_at else None,
            }
            for entry in daily_entries
        ]

        return {"success": True, "count": len(result), "days": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching daily entries: {str(e)}") from e


@router.get(
    "/api/energy-schedule/months/{month_sheet_id}/days",
    response_model=dict[str, Any],
    summary="List days for energy schedule month",
    description="Returns all daily entries and DOR/SCH calculation fields for a month sheet.",
)
async def get_energy_schedule_days_by_month(
    month_sheet_id: int,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return all daily entries for a month sheet."""
    try:
        daily_entries = get_all_daily_entries(db, month_sheet_id)

        result = []
        for entry in daily_entries:
            result.append(
                {
                    "id": entry.id,
                    "trading_date": entry.trading_date.isoformat(),
                    "day_of_month": entry.day_of_month,
                    "gdam": {
                        "nldc_fee": entry.gdam_nldc_fee,
                        "ctu_charges": entry.gdam_ctu_charges,
                        "cost": entry.gdam_cost,
                        "scheduled_mwh": entry.gdam_scheduled_quantity_mwh,
                    },
                    "dam": {
                        "nldc_fee": entry.dam_nldc_fee,
                        "ctu_charges": entry.dam_ctu_charges,
                        "cost": entry.dam_cost,
                        "scheduled_mwh": entry.dam_scheduled_quantity_mwh,
                    },
                    "rtm": {
                        "nldc_fee": entry.rtm_nldc_fee,
                        "ctu_charges": entry.rtm_ctu_charges,
                        "cost": entry.rtm_cost,
                        "scheduled_mwh": entry.rtm_scheduled_quantity_mwh,
                    },
                    "consumption_after_losses_mwh": entry.total_consumption_after_losses_mwh,
                    "regional_loss_percent": entry.regional_loss_percent,
                    "state_loss_percent": entry.state_loss_percent,
                    "combined_loss_percent": entry.combined_loss_percent,
                    "total_scheduled_mwh": entry.total_scheduled_mwh,
                    "ctu_losses_percent": entry.ctu_losses_percent,
                    "ctu_losses_mwh": entry.ctu_losses_mwh,
                    "energy_savings_mwh": entry.energy_savings_mwh,
                    "total_nldc_fee": entry.total_nldc_fee,
                    "total_ctu_charges": entry.total_ctu_charges,
                    "total_cost": entry.total_cost,
                    "is_complete": entry.is_complete,
                    "has_gdam_data": entry.has_gdam_data,
                    "has_dam_data": entry.has_dam_data,
                    "has_rtm_data": entry.has_rtm_data,
                    "has_sch_data": entry.has_sch_data,
                    "calculated_at": entry.calculated_at.isoformat() if entry.calculated_at else None,
                }
            )

        return {"success": True, "count": len(result), "daily_entries": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching daily entries: {str(e)}") from e

