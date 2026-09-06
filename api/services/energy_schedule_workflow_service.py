"""Admin workflow status for Energy Schedule Excel automation."""

from __future__ import annotations

import calendar
import math
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta
from typing import Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from api.services.energy_excel_calculation_service import CALCULATION_VERSION
from database.energy_schedule_builder import rebuild_energy_schedule_for_day
from database.models import DailyFile, EnergyScheduleConsumption, EnergyScheduleDay, EnergyScheduleMonth, MonthlyCalculation, Transaction

REQUIRED_UPLOAD_GROUPS = ("DOR-GDAM", "DOR-DAM", "DOR-RTM", "SCH")


def _month_bounds(year: int, month: int) -> tuple[date, date, int]:
    days = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, days), days


def _upload_group(file: DailyFile) -> str:
    if file.main_category == "DOR":
        return f"DOR-{file.sub_category or 'UNKNOWN'}"
    if file.main_category == "SCH":
        return "SCH"
    return file.report_type or file.main_category or "UNKNOWN"


def _status(present: int, expected: int) -> str:
    if expected <= 0:
        return "waiting"
    if present >= expected:
        return "complete"
    if present > 0:
        return "partial"
    return "waiting"


def build_workflow_status(db: Session, portfolio_id: int, year: int, month: int, mode: str = "compare") -> dict[str, Any]:
    start_date, end_date, calendar_days = _month_bounds(year, month)

    files = db.query(DailyFile).filter(
        and_(
            DailyFile.portfolio_id == portfolio_id,
            DailyFile.trading_date >= start_date,
            DailyFile.trading_date <= end_date,
        )
    ).all()
    upload_dates = sorted({item.trading_date for item in files})
    review_dates = upload_dates or [date(year, month, day) for day in range(1, calendar_days + 1)]

    files_by_date: dict[date, set[str]] = defaultdict(set)
    file_count_by_group: Counter[str] = Counter()
    for item in files:
        group = _upload_group(item)
        files_by_date[item.trading_date].add(group)
        file_count_by_group[group] += 1

    upload_rows = []
    for item_date in review_dates:
        present_groups = sorted(files_by_date.get(item_date, set()))
        missing_groups = [group for group in REQUIRED_UPLOAD_GROUPS if group not in present_groups]
        upload_rows.append(
            {
                "date": item_date.isoformat(),
                "present_groups": present_groups,
                "missing_groups": missing_groups,
                "ready": not missing_groups,
            }
        )

    month_sheet = db.query(EnergyScheduleMonth).filter(
        EnergyScheduleMonth.portfolio_id == portfolio_id,
        EnergyScheduleMonth.year == year,
        EnergyScheduleMonth.month == month,
    ).first()
    energy_rows = []
    energy_days: list[EnergyScheduleDay] = []
    if month_sheet:
        energy_days = db.query(EnergyScheduleDay).filter(
            EnergyScheduleDay.month_sheet_id == month_sheet.id,
            EnergyScheduleDay.trading_date >= start_date,
            EnergyScheduleDay.trading_date <= end_date,
        ).order_by(EnergyScheduleDay.trading_date.asc()).all()
        energy_rows = [
            {
                "date": row.trading_date.isoformat(),
                "ready": bool(row.is_complete),
                "has_gdam": bool(row.has_gdam_data),
                "has_dam": bool(row.has_dam_data),
                "has_rtm": bool(row.has_rtm_data),
                "has_sch": bool(row.has_sch_data),
                "total_scheduled_mwh": float(row.total_scheduled_mwh or 0.0),
                "total_cost": float(row.total_cost or 0.0),
            }
            for row in energy_days
        ]

    consumption_rows = db.query(EnergyScheduleConsumption).filter(
        EnergyScheduleConsumption.portfolio_id == portfolio_id,
        EnergyScheduleConsumption.consumption_date >= start_date,
        EnergyScheduleConsumption.consumption_date <= end_date,
    ).order_by(EnergyScheduleConsumption.consumption_date.asc()).all()
    consumption_dates = {row.consumption_date for row in consumption_rows}
    consumption_expected_dates = review_dates
    missing_consumption = [item.isoformat() for item in consumption_expected_dates if item not in consumption_dates]
    source_counts = Counter(row.source or "manual" for row in consumption_rows)

    calculation_type = f"{CALCULATION_VERSION}:{mode}"
    monthly_type = f"{CALCULATION_VERSION}:monthly:{mode}"
    calc_rows = db.query(MonthlyCalculation).filter(
        MonthlyCalculation.portfolio_id == portfolio_id,
        MonthlyCalculation.year == year,
        MonthlyCalculation.month == month,
        MonthlyCalculation.calculation_type == calculation_type,
    ).all()
    monthly_summary = db.query(MonthlyCalculation).filter(
        MonthlyCalculation.portfolio_id == portfolio_id,
        MonthlyCalculation.year == year,
        MonthlyCalculation.month == month,
        MonthlyCalculation.calculation_type == monthly_type,
    ).first()
    latest = [row.calculated_at for row in calc_rows if row.calculated_at]
    if monthly_summary and monthly_summary.calculated_at:
        latest.append(monthly_summary.calculated_at)

    ready_upload_days = sum(1 for row in upload_rows if row["ready"])
    ready_energy_days = sum(1 for row in energy_rows if row["ready"])
    expected_days = len(review_dates)

    return {
        "success": True,
        "portfolio_id": portfolio_id,
        "year": year,
        "month": month,
        "mode": mode,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "calendar_days": calendar_days,
            "workflow_days": expected_days,
        },
        "steps": {
            "uploads": {
                "status": _status(ready_upload_days, expected_days),
                "file_count": len(files),
                "uploaded_days": len(upload_dates),
                "ready_days": ready_upload_days,
                "missing_days": [row["date"] for row in upload_rows if not row["ready"]],
                "file_count_by_group": dict(file_count_by_group),
                "rows": upload_rows,
            },
            "energy_schedule": {
                "status": _status(ready_energy_days, expected_days),
                "ready_days": ready_energy_days,
                "stored_days": len(energy_days),
                "missing_days": [row["date"] for row in upload_rows if row["date"] not in {item["date"] for item in energy_rows}],
                "rows": energy_rows,
            },
            "consumption": {
                "status": _status(len(consumption_dates), expected_days),
                "stored_days": len(consumption_dates),
                "missing_days": missing_consumption,
                "source_counts": dict(source_counts),
            },
            "calculation": {
                "status": "complete" if monthly_summary else _status(len(calc_rows), expected_days),
                "saved_daily_rows": len(calc_rows),
                "monthly_summary_present": bool(monthly_summary),
                "latest_calculated_at": max(latest).isoformat() if latest else None,
                "complete_days": (monthly_summary.calculation_data or {}).get("completion", {}).get("complete_days") if monthly_summary else None,
                "missing_inputs": (monthly_summary.calculation_data or {}).get("completion", {}).get("missing_inputs") if monthly_summary else None,
            },
            "reports": {
                "status": "ready" if monthly_summary else "waiting",
                "excel_available": bool(monthly_summary),
                "pdf_available": bool(monthly_summary),
            },
        },
    }


def rebuild_workflow_energy_schedule(db: Session, portfolio_id: int, year: int, month: int) -> dict[str, Any]:
    start_date, end_date, _ = _month_bounds(year, month)
    dates = [
        row[0]
        for row in db.query(DailyFile.trading_date)
        .filter(
            DailyFile.portfolio_id == portfolio_id,
            DailyFile.trading_date >= start_date,
            DailyFile.trading_date <= end_date,
        )
        .distinct()
        .order_by(DailyFile.trading_date.asc())
        .all()
    ]
    results = [rebuild_energy_schedule_for_day(db, portfolio_id, item_date) for item_date in dates]
    return {
        "success": True,
        "portfolio_id": portfolio_id,
        "year": year,
        "month": month,
        "days_processed": len(results),
        "complete_days": sum(1 for item in results if item.get("is_complete")),
        "results": results,
    }



def seed_workflow_mock_data(db: Session, portfolio_id: int, year: int, month: int, days: int = 3) -> dict[str, Any]:
    """Create controlled synthetic workflow data for the first N days of a month."""
    _, _, calendar_days = _month_bounds(year, month)
    day_numbers = range(1, min(days, calendar_days) + 1)
    counts = {"daily_files_created": 0, "transactions_created": 0, "consumption_upserted": 0}

    for day_number in day_numbers:
        trading_date = date(year, month, day_number)
        for report_type, market, transaction_type in [
            ("DOR-GDAM", "GDAM", "buy"),
            ("DOR-DAM", "DAM", "buy"),
            ("DOR-RTM", "RTM", "buy"),
            ("SCH-DAM", "DAM", "scheduling"),
        ]:
            daily_file = db.query(DailyFile).filter(
                DailyFile.portfolio_id == portfolio_id,
                DailyFile.trading_date == trading_date,
                DailyFile.report_type == report_type,
            ).first()
            if daily_file is None:
                daily_file = DailyFile(
                    portfolio_id=portfolio_id,
                    trading_date=trading_date,
                    delivery_date=trading_date,
                    main_category=report_type.split("-")[0],
                    sub_category=market,
                    report_type=report_type,
                    original_filename=f"workflow-demo-{year}-{month:02d}-{day_number:02d}-{report_type}.json",
                    file_path="synthetic://energy-workflow-demo-v1",
                    charges={
                        "nldc_application_fee": 5.0 + day_number,
                        "ctu_transmission_charges": 115.0 + day_number * 4,
                    },
                    file_metadata={"is_synthetic": True, "scenario": "energy-workflow-demo-v1"},
                    parsed_at=datetime.now(),
                )
                db.add(daily_file)
                db.flush()
                counts["daily_files_created"] += 1
            if db.query(Transaction).filter(Transaction.daily_file_id == daily_file.id).count() > 0:
                continue
            for block in range(96):
                start = datetime.combine(trading_date, time.min) + timedelta(minutes=15 * block)
                market_factor = {"GDAM": 0.42, "DAM": 0.95, "RTM": 0.28}[market]
                wave = max(0.0, math.sin((block - 24) / 18))
                quantity = market_factor + day_number * 0.04 + wave * 0.18
                rate = 3200 + day_number * 75 + {"GDAM": 250, "DAM": 500, "RTM": 700}[market]
                db.add(Transaction(
                    daily_file_id=daily_file.id,
                    date=trading_date,
                    time_slot=f"{start:%H:%M} - {(start + timedelta(minutes=15)):%H:%M}",
                    time_block_start=start,
                    time_block_end=start + timedelta(minutes=15),
                    transaction_type=transaction_type,
                    quantity_mw=round(quantity, 4) if transaction_type == "buy" else 0.0,
                    rate_per_mwh=round(rate, 2) if transaction_type == "buy" else 0.0,
                    amount=round(quantity * rate / 4, 2) if transaction_type == "buy" else 0.0,
                    regional_drawal_mw=round(quantity * 1.02, 4) if transaction_type == "scheduling" else 0.0,
                    interface_drawal_mw=round(quantity * 0.96, 4) if transaction_type == "scheduling" else 0.0,
                    net_scheduled_mw=round(quantity * 0.96, 4) if transaction_type == "scheduling" else 0.0,
                ))
                counts["transactions_created"] += 1

        existing = db.query(EnergyScheduleConsumption).filter(
            EnergyScheduleConsumption.portfolio_id == portfolio_id,
            EnergyScheduleConsumption.consumption_date == trading_date,
        ).first()
        if existing is None:
            existing = EnergyScheduleConsumption(portfolio_id=portfolio_id, consumption_date=trading_date)
            db.add(existing)
        existing.c1_kwh = 1800 + day_number * 120
        existing.c2_kwh = 9500 + day_number * 250
        existing.c4_kwh = 18500 + day_number * 300
        existing.c5_kwh = 4200 + day_number * 180
        existing.base_tariff_per_unit = 8.5 if day_number % 2 == 0 else 7.5
        existing.source = "workflow-demo-seed"
        existing.notes = "Synthetic admin workflow demo data. Replace with client consumption before production use."
        counts["consumption_upserted"] += 1

    db.commit()
    rebuild_result = rebuild_workflow_energy_schedule(db, portfolio_id, year, month)
    return {"success": True, "portfolio_id": portfolio_id, "year": year, "month": month, "days_seeded": len(list(day_numbers)), **counts, "rebuild": rebuild_result}
