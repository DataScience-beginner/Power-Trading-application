from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from excel_consumption_service.models.workbook import (
    CalculationRun,
    DailyConsumptionRecord,
    SolarDailyRecord,
    SolarWorkingResult,
)


@dataclass(slots=True)
class SolarWorkingInputs:
    """Input values needed to calculate one workbook's Solar Working output."""

    tenant_id: str
    workbook_id: str


def calculate_solar_working(db: Session, inputs: SolarWorkingInputs) -> dict[str, object]:
    """Create deterministic Solar Working rows from normalized source data."""

    calculation_run = CalculationRun(
        tenant_id=inputs.tenant_id,
        workbook_upload_id=inputs.workbook_id,
        calculation_type="solar-working",
        status="running",
        started_at=datetime.now(UTC),
    )
    db.add(calculation_run)

    daily_values = list(
        db.scalars(
            select(DailyConsumptionRecord).where(
                DailyConsumptionRecord.workbook_upload_id == inputs.workbook_id
            )
        )
    )
    solar_values = list(
        db.scalars(
            select(SolarDailyRecord).where(
                SolarDailyRecord.workbook_upload_id == inputs.workbook_id
            )
        )
    )

    db.execute(
        delete(SolarWorkingResult).where(
            SolarWorkingResult.workbook_upload_id == inputs.workbook_id
        )
    )

    tneb_categories = defaultdict(lambda: {"C1": 0.0, "C2": 0.0, "C4": 0.0, "C5": 0.0})
    iex_categories = defaultdict(lambda: {"C1": 0.0, "C2": 0.0, "C4": 0.0, "C5": 0.0})
    direct_tneb_totals = defaultdict(float)
    solar_totals = defaultdict(float)

    for record in daily_values:
        if record.metric_name == "tneb_category_total" and record.category_code in tneb_categories[record.reading_date]:
            tneb_categories[record.reading_date][record.category_code] = record.value
        elif record.metric_name == "tneb_total_consumption":
            direct_tneb_totals[record.reading_date] = record.value
        elif record.metric_name == "iex_category_total" and record.category_code in iex_categories[record.reading_date]:
            iex_categories[record.reading_date][record.category_code] += record.value

    for record in solar_values:
        solar_totals[record.reading_date] += record.value

    all_dates = sorted(
        set(tneb_categories.keys())
        | set(iex_categories.keys())
        | set(solar_totals.keys())
        | set(direct_tneb_totals.keys())
    )

    created_rows = []
    for reading_date in all_dates:
        tneb_values = tneb_categories[reading_date]
        iex_values = iex_categories[reading_date]
        tneb_total = sum(tneb_values.values())
        if tneb_total == 0 and direct_tneb_totals[reading_date] > 0:
            tneb_total = direct_tneb_totals[reading_date]
        iex_total = sum(iex_values.values())
        solar_total = solar_totals[reading_date]
        post_iex_balance = tneb_total - iex_total
        tneb_balance = post_iex_balance - solar_total
        banking_balance = solar_total - post_iex_balance

        created_rows.append(
            SolarWorkingResult(
                tenant_id=inputs.tenant_id,
                workbook_upload_id=inputs.workbook_id,
                reading_date=reading_date,
                tneb_c1=tneb_values["C1"],
                tneb_c2=tneb_values["C2"],
                tneb_c4=tneb_values["C4"],
                tneb_c5=tneb_values["C5"],
                tneb_total=tneb_total,
                iex_c1=iex_values["C1"],
                iex_c2=iex_values["C2"],
                iex_c4=iex_values["C4"],
                iex_c5=iex_values["C5"],
                iex_total=iex_total,
                post_iex_balance=post_iex_balance,
                solar_total=solar_total,
                tneb_balance=tneb_balance,
                banking_balance=banking_balance,
            )
        )

    db.add_all(created_rows)
    calculation_run.status = "completed"
    calculation_run.completed_at = datetime.now(UTC)
    calculation_run.summary = (
        f"Created {len(created_rows)} Solar Working rows for workbook {inputs.workbook_id}."
    )
    db.flush()

    return {
        "status": "completed",
        "row_count": len(created_rows),
        "date_from": all_dates[0].isoformat() if all_dates else None,
        "date_to": all_dates[-1].isoformat() if all_dates else None,
    }


def load_solar_working_rows(
    db: Session,
    workbook_id: str,
    limit: int | None,
) -> list[SolarWorkingResult]:
    """Load calculated rows in date order for APIs and verification scripts."""

    query = (
        select(SolarWorkingResult)
        .where(SolarWorkingResult.workbook_upload_id == workbook_id)
        .order_by(SolarWorkingResult.reading_date)
    )
    if limit is not None:
        query = query.limit(limit)
    return list(db.scalars(query))
