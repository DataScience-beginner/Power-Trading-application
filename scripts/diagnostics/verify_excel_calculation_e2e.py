"""Verify the Excel-conversion workflow from upload through calculation.

This diagnostic intentionally uses local/mock workbook uploads and local
database state. It does not send any workbook or report to a client.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from io import StringIO
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from sqlalchemy import and_

from api.main import app
from api.schemas.energy_excel_calculation import ConsumptionEntry
from api.services.energy_excel_calculation_service import (
    build_calculation_inputs,
    calculate_savings_sheet,
    calculate_slot_wise_consolidate,
    compare_daily,
    run_calculation,
    upsert_consumption,
)
from database.config import Base, SessionLocal, engine
from database.models import (
    DailyFile,
    EnergyScheduleConsumption,
    EnergyScheduleDay,
    MonthlyCalculation,
    Portfolio,
    Transaction,
)


MOCK_DIR = PROJECT_ROOT / "Data" / "mock_reports"
TARGET_DATES = [date(2026, 1, day) for day in (1, 2, 3)]


def target_filenames(trading_date: date) -> list[str]:
    """Return mock report filenames for one diagnostic date."""
    stamp = trading_date.strftime("%d%m%y")
    return [
        f"GDAM_IEX{stamp}DOR_NPT0027_KA0_Mellbro_Sugars_Pvt.xlsx",
        f"DAM_IEX{stamp}DOR_NPT0027_KA0_Mellbro_Sugars_Pvt.xlsx",
        f"RTM_IEX{stamp}DOR_NPT0027_KA0_Mellbro_Sugars_Pvt.xlsx",
        f"IEX{stamp}SCH_NPT0027_KA0_Mellbro_Sugars_Pvt.xlsx",
    ]


def upload_mock_reports() -> list[dict[str, Any]]:
    """Upload the selected workbook files through the API upload route."""
    client = TestClient(app)
    responses: list[dict[str, Any]] = []

    for trading_date in TARGET_DATES:
        for filename in target_filenames(trading_date):
            path = MOCK_DIR / filename
            if not path.exists():
                raise FileNotFoundError(path)
            with path.open("rb") as handle:
                captured = StringIO()
                with redirect_stdout(captured), redirect_stderr(captured):
                    response = client.post(
                        "/api/upload",
                        files={
                            "file": (
                                filename,
                                handle,
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            )
                        },
                    )
            payload = response.json()
            responses.append(
                {
                    "filename": filename,
                    "trading_date": trading_date.isoformat(),
                    "status_code": response.status_code,
                    "success": payload.get("success"),
                    "report_type": payload.get("summary", {}).get("report_type"),
                    "portfolio_id": payload.get("database", {}).get("portfolio_id"),
                    "transactions_saved": payload.get("database", {}).get("transactions_saved"),
                    "energy_schedule": payload.get("energy_schedule"),
                    "captured_log_lines": len(captured.getvalue().splitlines()),
                    "error": payload.get("detail") or payload.get("error"),
                }
            )
            if response.status_code >= 400 or not payload.get("success"):
                raise RuntimeError(json.dumps(responses[-1], indent=2, default=str))

    return responses


def compact_summary(result: dict[str, Any]) -> dict[str, Any]:
    """Return the compact readiness signal used in normal development loops."""
    upload_report_types = Counter(item["report_type"] for item in result["uploads"])
    return {
        "success": result["success"],
        "target_dates": result["target_dates"],
        "portfolio_id": result["portfolio_id"],
        "uploads": {
            "files": len(result["uploads"]),
            "successful": sum(1 for item in result["uploads"] if item["success"]),
            "report_types": dict(upload_report_types),
            "transactions_saved": sum(item["transactions_saved"] or 0 for item in result["uploads"]),
            "captured_log_lines": sum(item["captured_log_lines"] for item in result["uploads"]),
        },
        "database_ready": result["database_ready"],
        "consumption": result["consumption"],
        "calculation": result["calculation"],
        "savings_sheet_totals": result["savings_sheet"]["totals"],
        "slot_wise_rows": result["slot_wise_consolidate"]["rows"],
    }


def pick_portfolio_id(db) -> int:
    """Use the portfolio that received the target-date mock uploads."""
    row = (
        db.query(DailyFile.portfolio_id)
        .filter(DailyFile.trading_date.in_(TARGET_DATES))
        .group_by(DailyFile.portfolio_id)
        .order_by(DailyFile.portfolio_id)
        .first()
    )
    if row:
        return int(row[0])

    portfolio = db.query(Portfolio).order_by(Portfolio.id).first()
    if not portfolio:
        raise RuntimeError("No portfolio was created by upload.")
    return int(portfolio.id)


def seed_consumption_if_missing(db, portfolio_id: int) -> int:
    """Seed deterministic test consumption when client data is absent."""
    seed_rows = [
        (TARGET_DATES[0], 1500.0, 9300.0, 18300.0, 5150.0, 7.5),
        (TARGET_DATES[1], 2050.0, 10000.0, 19250.0, 3650.0, 8.5),
        (TARGET_DATES[2], 1800.0, 10650.0, 20350.0, 3800.0, 8.5),
    ]
    records = []
    for trading_date, c1, c2, c4, c5, tariff in seed_rows:
        existing = (
            db.query(EnergyScheduleConsumption)
            .filter(
                and_(
                    EnergyScheduleConsumption.portfolio_id == portfolio_id,
                    EnergyScheduleConsumption.consumption_date == trading_date,
                )
            )
            .first()
        )
        if not existing:
            records.append(
                ConsumptionEntry(
                    portfolio_id=portfolio_id,
                    consumption_date=trading_date,
                    c1_kwh=c1,
                    c2_kwh=c2,
                    c4_kwh=c4,
                    c5_kwh=c5,
                    base_tariff_per_unit=tariff,
                    source="diagnostic-seed",
                    notes="Seeded by verify_excel_calculation_e2e.py for backend readiness testing.",
                )
            )
    if records:
        upsert_consumption(db, records)
    return len(records)


def verify() -> dict[str, Any]:
    """Run the diagnostic and return a compact audit summary."""
    Base.metadata.create_all(bind=engine)
    upload_results = upload_mock_reports()

    db = SessionLocal()
    try:
        portfolio_id = pick_portfolio_id(db)
        consumption_seeded_count = seed_consumption_if_missing(db, portfolio_id)

        files = (
            db.query(DailyFile)
            .filter(
                DailyFile.portfolio_id == portfolio_id,
                DailyFile.trading_date.in_(TARGET_DATES),
            )
            .order_by(DailyFile.report_type)
            .all()
        )
        file_counts = Counter(file.report_type for file in files)
        transaction_count = (
            db.query(Transaction)
            .join(DailyFile)
            .filter(
                DailyFile.portfolio_id == portfolio_id,
                DailyFile.trading_date.in_(TARGET_DATES),
            )
            .count()
        )
        energy_days = (
            db.query(EnergyScheduleDay)
            .join(EnergyScheduleDay.month_sheet)
            .filter(EnergyScheduleDay.trading_date.in_(TARGET_DATES))
            .filter_by(portfolio_id=portfolio_id)
            .order_by(EnergyScheduleDay.trading_date)
            .all()
        )
        if len(energy_days) != len(TARGET_DATES):
            raise RuntimeError("Upload did not create all expected EnergyScheduleDay rows.")

        calculation_results = []
        for trading_date in TARGET_DATES:
            calculation_results.extend(
                run_calculation(
                    db,
                    portfolio_id=portfolio_id,
                    year=trading_date.year,
                    month=trading_date.month,
                    day=trading_date.day,
                    mode="compare",
                )
            )
        daily_inputs = [build_calculation_inputs(db, portfolio_id, trading_date) for trading_date in TARGET_DATES]
        comparisons = [compare_daily(daily_input) for daily_input in daily_inputs]
        savings_sheet = calculate_savings_sheet(comparisons)
        slot_wise = calculate_slot_wise_consolidate(daily_inputs)
        monthly_calculation_count = (
            db.query(MonthlyCalculation)
            .filter(
                MonthlyCalculation.portfolio_id == portfolio_id,
                MonthlyCalculation.calculation_date.in_(TARGET_DATES),
                MonthlyCalculation.calculation_type.like("excel-conversion-v1:%"),
            )
            .count()
        )

        output_has_break = any(
            value in {"#DIV/0!", "#REF!", "#VALUE!", "#NAME?", "#N/A"}
            for comparison in comparisons
            for value in [
                comparison.corrected.b44_iex_price,
                comparison.corrected.b45_iex_price_per_unit,
                comparison.corrected.b46_eb_price,
                comparison.corrected.b47_eb_price_per_unit,
            ]
        )

        return {
            "success": True,
            "target_dates": [item.isoformat() for item in TARGET_DATES],
            "portfolio_id": portfolio_id,
            "uploads": upload_results,
            "database_ready": {
                "daily_files": len(files),
                "report_types": dict(file_counts),
                "transactions": transaction_count,
                "energy_schedule_days": [
                    {
                        "id": energy_day.id,
                        "trading_date": energy_day.trading_date.isoformat(),
                        "has_gdam_data": bool(energy_day.has_gdam_data),
                        "has_dam_data": bool(energy_day.has_dam_data),
                        "has_rtm_data": bool(energy_day.has_rtm_data),
                        "has_sch_data": bool(energy_day.has_sch_data),
                        "is_complete": bool(energy_day.is_complete),
                        "total_scheduled_mwh": energy_day.total_scheduled_mwh,
                        "total_consumption_after_losses_mwh": energy_day.total_consumption_after_losses_mwh,
                        "total_cost": energy_day.total_cost,
                    }
                    for energy_day in energy_days
                ],
            },
            "consumption": {
                "seeded_count": consumption_seeded_count,
                "present_days": sum(1 for daily_input in daily_inputs if daily_input.consumption is not None),
                "sources": sorted(
                    {
                        daily_input.consumption.source
                        for daily_input in daily_inputs
                        if daily_input.consumption is not None
                    }
                ),
            },
            "calculation": {
                "days_processed": len(calculation_results),
                "persisted_count": monthly_calculation_count,
                "complete_days": sum(1 for comparison in comparisons if comparison.corrected.is_complete),
                "missing_inputs_by_day": {
                    comparison.trading_date.isoformat(): comparison.corrected.missing_inputs
                    for comparison in comparisons
                },
                "daily_outputs": [
                    {
                        "trading_date": comparison.trading_date.isoformat(),
                        "b44_iex_price": comparison.corrected.b44_iex_price,
                        "b45_iex_price_per_unit": comparison.corrected.b45_iex_price_per_unit,
                        "b46_eb_price": comparison.corrected.b46_eb_price,
                        "b47_eb_price_per_unit": comparison.corrected.b47_eb_price_per_unit,
                        "cost_saving": comparison.corrected.cost_saving,
                    }
                    for comparison in comparisons
                ],
                "output_has_break": output_has_break,
            },
            "savings_sheet": {
                "rows": len(savings_sheet.rows),
                "totals": savings_sheet.totals,
            },
            "slot_wise_consolidate": {
                "rows": [row.model_dump() for row in slot_wise.rows],
            },
        }
    finally:
        db.close()


if __name__ == "__main__":
    print(json.dumps(compact_summary(verify()), indent=2, default=str))
