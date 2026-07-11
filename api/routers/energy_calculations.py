"""Energy schedule calculation summary routes."""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import EnergyScheduleDay, EnergyScheduleMonth


router = APIRouter(tags=["energy-calculations"])


def _complete_entries(
    db: Session,
    portfolio_id: Optional[int],
    year: Optional[int],
    month: Optional[int],
) -> list[EnergyScheduleDay]:
    """Return complete energy schedule day entries filtered by portfolio/year/month."""
    query = db.query(EnergyScheduleDay).join(EnergyScheduleMonth)

    if portfolio_id:
        query = query.filter(EnergyScheduleMonth.portfolio_id == portfolio_id)
    if year:
        query = query.filter(EnergyScheduleMonth.year == year)
    if month:
        query = query.filter(EnergyScheduleMonth.month == month)

    return query.filter(EnergyScheduleDay.is_complete == 1).order_by(EnergyScheduleDay.trading_date).all()


@router.get(
    "/api/energy-schedule/calculations/ctu-losses",
    response_model=dict[str, Any],
    summary="Analyze CTU losses",
    description="Returns CTU loss totals, averages, and day-wise breakdown for complete energy schedule entries.",
)
async def get_ctu_losses_analysis(
    portfolio_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return CTU losses analysis for a filtered period."""
    try:
        entries = _complete_entries(db, portfolio_id, year, month)

        if not entries:
            return {
                "success": True,
                "summary": {
                    "total_scheduled_mwh": 0,
                    "total_losses_mwh": 0,
                    "average_ctu_losses_percent": 0,
                    "days_analyzed": 0,
                },
                "daily_breakdown": [],
                "message": "No complete entries found for the specified period",
            }

        total_scheduled = sum(e.total_scheduled_mwh for e in entries)
        total_losses = sum(e.ctu_losses_mwh for e in entries)
        avg_ctu_losses_percent = (total_losses / total_scheduled * 100) if total_scheduled > 0 else 0

        return {
            "success": True,
            "summary": {
                "total_scheduled_mwh": total_scheduled,
                "total_losses_mwh": total_losses,
                "average_ctu_losses_percent": avg_ctu_losses_percent,
                "days_analyzed": len(entries),
            },
            "daily_breakdown": [
                {
                    "date": entry.trading_date.isoformat(),
                    "scheduled_mwh": entry.total_scheduled_mwh,
                    "consumption_mwh": entry.total_consumption_after_losses_mwh,
                    "ctu_losses_mwh": entry.ctu_losses_mwh,
                    "ctu_losses_percent": entry.ctu_losses_percent,
                }
                for entry in entries
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating CTU losses: {str(e)}") from e


@router.get(
    "/api/energy-schedule/calculations/ctu-charges",
    response_model=dict[str, Any],
    summary="Summarize CTU charges",
    description="Aggregates GDAM, DAM, RTM, and total CTU charges across complete energy schedule entries.",
)
async def get_ctu_charges_summary(
    portfolio_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return CTU charge summary by market and day."""
    try:
        entries = _complete_entries(db, portfolio_id, year, month)

        if not entries:
            return {
                "success": True,
                "summary": {
                    "total_gdam_ctu_charges": 0,
                    "total_dam_ctu_charges": 0,
                    "total_rtm_ctu_charges": 0,
                    "total_ctu_charges": 0,
                    "days_analyzed": 0,
                },
                "daily_breakdown": [],
                "message": "No complete entries found for the specified period",
            }

        return {
            "success": True,
            "summary": {
                "total_gdam_ctu_charges": sum(e.gdam_ctu_charges for e in entries),
                "total_dam_ctu_charges": sum(e.dam_ctu_charges for e in entries),
                "total_rtm_ctu_charges": sum(e.rtm_ctu_charges for e in entries),
                "total_ctu_charges": sum(e.total_ctu_charges for e in entries),
                "days_analyzed": len(entries),
            },
            "daily_breakdown": [
                {
                    "date": entry.trading_date.isoformat(),
                    "gdam_ctu_charges": entry.gdam_ctu_charges,
                    "dam_ctu_charges": entry.dam_ctu_charges,
                    "rtm_ctu_charges": entry.rtm_ctu_charges,
                    "total_ctu_charges": entry.total_ctu_charges,
                }
                for entry in entries
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating CTU charges: {str(e)}") from e


@router.get(
    "/api/energy-schedule/calculations/nldc-fees",
    response_model=dict[str, Any],
    summary="Summarize NLDC fees",
    description="Aggregates GDAM, DAM, RTM, and total NLDC fees across complete energy schedule entries.",
)
async def get_nldc_fees_summary(
    portfolio_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return NLDC fee summary by market and day."""
    try:
        entries = _complete_entries(db, portfolio_id, year, month)

        if not entries:
            return {
                "success": True,
                "summary": {
                    "total_gdam_nldc_fees": 0,
                    "total_dam_nldc_fees": 0,
                    "total_rtm_nldc_fees": 0,
                    "total_nldc_fees": 0,
                    "days_analyzed": 0,
                },
                "daily_breakdown": [],
                "message": "No complete entries found for the specified period",
            }

        return {
            "success": True,
            "summary": {
                "total_gdam_nldc_fees": sum(e.gdam_nldc_fee for e in entries),
                "total_dam_nldc_fees": sum(e.dam_nldc_fee for e in entries),
                "total_rtm_nldc_fees": sum(e.rtm_nldc_fee for e in entries),
                "total_nldc_fees": sum(e.total_nldc_fee for e in entries),
                "days_analyzed": len(entries),
            },
            "daily_breakdown": [
                {
                    "date": entry.trading_date.isoformat(),
                    "gdam_nldc_fee": entry.gdam_nldc_fee,
                    "dam_nldc_fee": entry.dam_nldc_fee,
                    "rtm_nldc_fee": entry.rtm_nldc_fee,
                    "total_nldc_fee": entry.total_nldc_fee,
                }
                for entry in entries
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating NLDC fees: {str(e)}") from e


@router.get(
    "/api/energy-schedule/calculations/energy-savings",
    response_model=dict[str, Any],
    summary="Summarize energy savings",
    description="Returns energy savings totals, cost totals, and day-wise trend data for complete entries.",
)
async def get_energy_savings_summary(
    portfolio_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return energy savings summary and trend data."""
    try:
        entries = _complete_entries(db, portfolio_id, year, month)

        if not entries:
            return {
                "success": True,
                "summary": {
                    "total_energy_savings_mwh": 0,
                    "total_scheduled_mwh": 0,
                    "total_consumption_mwh": 0,
                    "total_cost": 0,
                    "average_savings_percent": 0,
                    "days_analyzed": 0,
                },
                "daily_breakdown": [],
                "message": "No complete entries found for the specified period",
            }

        total_energy_savings = sum(e.energy_savings_mwh for e in entries)
        total_scheduled = sum(e.total_scheduled_mwh for e in entries)
        total_consumption = sum(e.total_consumption_after_losses_mwh for e in entries)
        total_cost = sum(e.total_cost for e in entries)

        return {
            "success": True,
            "summary": {
                "total_energy_savings_mwh": total_energy_savings,
                "total_scheduled_mwh": total_scheduled,
                "total_consumption_mwh": total_consumption,
                "total_cost": total_cost,
                "average_savings_percent": (
                    total_energy_savings / total_scheduled * 100
                )
                if total_scheduled > 0
                else 0,
                "days_analyzed": len(entries),
            },
            "daily_breakdown": [
                {
                    "date": entry.trading_date.isoformat(),
                    "scheduled_mwh": entry.total_scheduled_mwh,
                    "consumption_mwh": entry.total_consumption_after_losses_mwh,
                    "energy_savings_mwh": entry.energy_savings_mwh,
                    "ctu_losses_percent": entry.ctu_losses_percent,
                    "total_cost": entry.total_cost,
                }
                for entry in entries
            ],
            "trend": {
                "min_savings": min(e.energy_savings_mwh for e in entries),
                "max_savings": max(e.energy_savings_mwh for e in entries),
                "avg_savings": total_energy_savings / len(entries),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating energy savings: {str(e)}") from e

