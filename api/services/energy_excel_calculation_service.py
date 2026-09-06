"""Backend Excel-conversion calculation service for energy schedules."""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterable

from sqlalchemy import and_
from sqlalchemy.orm import Session

from api.schemas.energy_excel_calculation import (
    ConsumptionEntry,
    DailyCalculationOutput,
    DailyComparisonOutput,
    SavingsSheetOutput,
    SavingsSheetRow,
    SlotWiseConsolidateOutput,
    SlotWiseConsolidateRow,
)
from database.models import (
    DailyFile,
    EnergyScheduleConsumption,
    EnergyScheduleDay,
    EnergyScheduleMonth,
    MonthlyCalculation,
    Transaction,
)


MARKETS = ("gdam", "dam", "rtm")
BUCKETS = ("c1", "c2", "c4", "c5")
CALCULATION_VERSION = "excel-conversion-v1"


@dataclass
class CalculationAssumptions:
    stu_loss_pct: float = 0.0234
    discom_loss_pct: float = 0.0195
    iex_transaction_charge_per_kwh: float = 0.02
    iex_transaction_gst_pct: float = 0.18
    default_ctu_charge: float = 122.94
    nldc_sched_charge_per_mwh: float = 1.0
    stu_transmission_charge_per_mwh: float = 260.0
    stu_scheduling_charge_fixed: float = 209.0
    stu_system_charge_per_mwh: float = 4.01
    trading_margin_per_kwh: float = 0.02
    css_per_kwh: float = 1.99
    asc_per_kwh: float = 0.0
    wheeling_charge_per_kwh: float = 1.04
    e_tax_per_kwh: float = 0.0
    rpo_charge_per_kwh: float = 0.12
    rpo_multiplier: float = 0.105
    tariff_tax_pct: float = 0.05
    default_base_tariff_per_unit: float = 8.5
    tolerance: float = 0.01


@dataclass
class MarketInput:
    market: str
    purchased_mwh: float = 0.0
    iex_payout: float = 0.0
    ctu_loss_pct: float = 0.0
    ctu_charge: float = 0.0
    nldc_fee: float = 0.0
    bucket_mwh: dict[str, float] = field(default_factory=dict)


@dataclass
class DailyCalculationInput:
    portfolio_id: int
    trading_date: date
    consumption: ConsumptionEntry | None
    markets: dict[str, MarketInput]


def numeric(value: Any) -> float:
    """Return a float for optional database values."""
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def safe_divide(numerator: float, denominator: float) -> float | None:
    """Corrected-mode division: no spreadsheet errors in API output."""
    if denominator == 0:
        return None
    return numerator / denominator


def parity_divide(numerator: float, denominator: float) -> float | str:
    """Excel-parity division: expose the same error shape for QA comparisons."""
    if denominator == 0:
        return "#DIV/0!"
    return numerator / denominator


def day_date(year: int, month: int, day: int) -> date:
    """Build a validated date from calculation scope parts."""
    return date(year, month, day)


def month_dates(year: int, month: int, day: int | None = None) -> list[date]:
    """Return the requested day or all dates in a month."""
    if day is not None:
        return [day_date(year, month, day)]
    return [date(year, month, item) for item in range(1, monthrange(year, month)[1] + 1)]


def upsert_consumption(db: Session, records: Iterable[ConsumptionEntry]) -> list[ConsumptionEntry]:
    """Create or update client-provided consumption rows."""
    saved: list[ConsumptionEntry] = []
    for record in records:
        existing = db.query(EnergyScheduleConsumption).filter(
            and_(
                EnergyScheduleConsumption.portfolio_id == record.portfolio_id,
                EnergyScheduleConsumption.consumption_date == record.consumption_date,
            )
        ).first()

        values = record.model_dump()
        if existing:
            for key, value in values.items():
                setattr(existing, key, value)
            row = existing
        else:
            row = EnergyScheduleConsumption(**values)
            db.add(row)
        saved.append(record)

    db.commit()
    return saved


def list_consumption(
    db: Session,
    portfolio_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[ConsumptionEntry]:
    """Read client-provided consumption rows."""
    query = db.query(EnergyScheduleConsumption).filter(EnergyScheduleConsumption.portfolio_id == portfolio_id)
    if start_date:
        query = query.filter(EnergyScheduleConsumption.consumption_date >= start_date)
    if end_date:
        query = query.filter(EnergyScheduleConsumption.consumption_date <= end_date)

    rows = query.order_by(EnergyScheduleConsumption.consumption_date).all()
    return [
        ConsumptionEntry(
            portfolio_id=row.portfolio_id,
            consumption_date=row.consumption_date,
            c1_kwh=numeric(row.c1_kwh),
            c2_kwh=numeric(row.c2_kwh),
            c4_kwh=numeric(row.c4_kwh),
            c5_kwh=numeric(row.c5_kwh),
            base_tariff_per_unit=row.base_tariff_per_unit,
            source=row.source or "manual",
            notes=row.notes,
        )
        for row in rows
    ]


def _slot_bucket(index: int) -> str:
    """Map 15-minute slot index to the workbook tariff bucket."""
    excel_row = index + 7
    if 31 <= excel_row <= 46:
        return "c1"
    if 79 <= excel_row <= 94:
        return "c2"
    if 27 <= excel_row <= 30 or 47 <= excel_row <= 78:
        return "c4"
    return "c5"


def _market_bucket_mwh(db: Session, portfolio_id: int, trading_date: date, market: str) -> dict[str, float]:
    """Summarize uploaded DOR quantities into workbook tariff buckets."""
    daily_file = db.query(DailyFile).filter(
        and_(
            DailyFile.portfolio_id == portfolio_id,
            DailyFile.trading_date == trading_date,
            DailyFile.main_category == "DOR",
            DailyFile.sub_category == market.upper(),
        )
    ).first()
    if not daily_file:
        return {}

    transactions = db.query(Transaction).filter(Transaction.daily_file_id == daily_file.id).order_by(
        Transaction.time_block_start,
        Transaction.id,
    ).all()
    buckets = {bucket: 0.0 for bucket in BUCKETS}
    for index, txn in enumerate(transactions[:96]):
        buckets[_slot_bucket(index)] += numeric(txn.quantity_mw) * 0.25
    return buckets


def _daily_entry(db: Session, portfolio_id: int, trading_date: date) -> EnergyScheduleDay | None:
    return db.query(EnergyScheduleDay).join(EnergyScheduleMonth).filter(
        and_(
            EnergyScheduleMonth.portfolio_id == portfolio_id,
            EnergyScheduleDay.trading_date == trading_date,
        )
    ).first()


def build_calculation_inputs(db: Session, portfolio_id: int, trading_date: date) -> DailyCalculationInput:
    """Build one daily input object from uploaded market data and client consumption."""
    day = _daily_entry(db, portfolio_id, trading_date)
    consumption = list_consumption(db, portfolio_id, trading_date, trading_date)
    markets: dict[str, MarketInput] = {}
    fallback_loss_pct = 0.0
    if day:
        fallback_loss_pct = numeric(day.combined_loss_percent) / 100 if numeric(day.combined_loss_percent) > 1 else numeric(day.combined_loss_percent)

    for market in MARKETS:
        scheduled = numeric(getattr(day, f"{market}_scheduled_quantity_mwh", 0.0)) if day else 0.0
        ctu_loss = fallback_loss_pct
        if day and numeric(day.ctu_losses_percent):
            ctu_loss = numeric(day.ctu_losses_percent) / 100

        markets[market] = MarketInput(
            market=market,
            purchased_mwh=scheduled,
            iex_payout=numeric(getattr(day, f"{market}_cost", 0.0)) if day else 0.0,
            ctu_loss_pct=ctu_loss,
            ctu_charge=numeric(getattr(day, f"{market}_ctu_charges", 0.0)) if day else 0.0,
            nldc_fee=numeric(getattr(day, f"{market}_nldc_fee", 0.0)) if day else 0.0,
            bucket_mwh=_market_bucket_mwh(db, portfolio_id, trading_date, market),
        )

    return DailyCalculationInput(
        portfolio_id=portfolio_id,
        trading_date=trading_date,
        consumption=consumption[0] if consumption else None,
        markets=markets,
    )


def calculate_delivery_after_losses(
    purchased_mwh: float,
    ctu_loss_pct: float,
    assumptions: CalculationAssumptions,
) -> dict[str, float]:
    """Convert MWh to kWh and apply CTU, STU, and discom losses."""
    total_kwh = purchased_mwh * 1000
    after_ctu = total_kwh * (1 - ctu_loss_pct)
    after_stu = after_ctu * (1 - assumptions.stu_loss_pct)
    delivered_at_bus = after_stu * (1 - assumptions.discom_loss_pct)
    return {
        "total_kwh": total_kwh,
        "after_ctu_kwh": after_ctu,
        "after_stu_kwh": after_stu,
        "delivered_at_bus_kwh": delivered_at_bus,
    }


def calculate_statutory_charges(
    market: MarketInput,
    delivered_at_bus_kwh: float,
    assumptions: CalculationAssumptions,
    *,
    parity_day: int | None = None,
) -> dict[str, float]:
    """Calculate the workbook statutory charge rows for one market."""
    purchased_kwh = market.purchased_mwh * 1000
    ctu_charge = market.ctu_charge or assumptions.default_ctu_charge
    stu_system_divisor = 1 if parity_day == 1 else 24
    rpo = 0.0 if market.market == "gdam" else delivered_at_bus_kwh * assumptions.rpo_charge_per_kwh * assumptions.rpo_multiplier

    rows = {
        "iex_transaction_charges": purchased_kwh
        * assumptions.iex_transaction_charge_per_kwh
        * (1 + assumptions.iex_transaction_gst_pct),
        "nldc_application_fee": market.nldc_fee,
        "ctu_transmission_charges": (ctu_charge / 250) * purchased_kwh,
        "nldc_sched_oprn_charges": market.purchased_mwh * assumptions.nldc_sched_charge_per_mwh,
        "stu_transmission_charges": market.purchased_mwh * assumptions.stu_transmission_charge_per_mwh,
        "stu_scheduling": assumptions.stu_scheduling_charge_fixed if market.purchased_mwh > 0 else 0.0,
        "stu_system_operating_charge": market.purchased_mwh * assumptions.stu_system_charge_per_mwh / stu_system_divisor,
        "trading_margin": market.purchased_mwh * assumptions.trading_margin_per_kwh * 1000,
        "css": delivered_at_bus_kwh * assumptions.css_per_kwh,
        "asc": delivered_at_bus_kwh * assumptions.asc_per_kwh,
        "wheeling_charges": delivered_at_bus_kwh * assumptions.wheeling_charge_per_kwh,
        "e_tax": delivered_at_bus_kwh * assumptions.e_tax_per_kwh,
        "rpo_charges": rpo,
    }
    rows["total_statutory_charges"] = sum(rows.values())
    return rows


def calculate_market_purchase(
    market: MarketInput,
    assumptions: CalculationAssumptions,
    *,
    parity_day: int | None = None,
) -> dict[str, Any]:
    """Calculate one market block from the daily workbook sheet."""
    delivery = calculate_delivery_after_losses(market.purchased_mwh, market.ctu_loss_pct, assumptions)
    charges = calculate_statutory_charges(
        market,
        delivery["delivered_at_bus_kwh"],
        assumptions,
        parity_day=parity_day,
    )
    total_cost = market.iex_payout + charges["total_statutory_charges"]
    return {
        "market": market.market,
        "purchased_mwh": market.purchased_mwh,
        "iex_payout": market.iex_payout,
        "delivery": delivery,
        "charges": charges,
        "total_cost": total_cost,
    }


def _tariffs(base_tariff: float, assumptions: CalculationAssumptions) -> dict[str, float]:
    return {
        "c1": base_tariff * 1.25 * (1 + assumptions.tariff_tax_pct),
        "c2": base_tariff * 1.25 * (1 + assumptions.tariff_tax_pct),
        "c4": base_tariff * (1 + assumptions.tariff_tax_pct),
        "c5": base_tariff * 0.95 * (1 + assumptions.tariff_tax_pct),
    }


def calculate_equivalent_eb_price(
    inputs: DailyCalculationInput,
    assumptions: CalculationAssumptions,
) -> dict[str, Any]:
    """Calculate the workbook equivalent EB cost from tariff-bucketed delivered units."""
    base_tariff = (
        inputs.consumption.base_tariff_per_unit
        if inputs.consumption and inputs.consumption.base_tariff_per_unit is not None
        else assumptions.default_base_tariff_per_unit
    )
    tariffs = _tariffs(base_tariff, assumptions)
    bucket_delivered_kwh = {bucket: 0.0 for bucket in BUCKETS}

    for market in inputs.markets.values():
        if any(market.bucket_mwh.values()):
            for bucket, mwh in market.bucket_mwh.items():
                bucket_delivery = calculate_delivery_after_losses(mwh, market.ctu_loss_pct, assumptions)
                bucket_delivered_kwh[bucket] += bucket_delivery["delivered_at_bus_kwh"]
        elif market.purchased_mwh:
            delivery = calculate_delivery_after_losses(market.purchased_mwh, market.ctu_loss_pct, assumptions)
            bucket_delivered_kwh["c1"] += delivery["delivered_at_bus_kwh"]

    bucket_costs = {bucket: bucket_delivered_kwh[bucket] * tariffs[bucket] for bucket in BUCKETS}
    return {
        "base_tariff_per_unit": base_tariff,
        "tariffs": tariffs,
        "bucket_delivered_kwh": bucket_delivered_kwh,
        "bucket_costs": bucket_costs,
        "total_delivered_kwh": sum(bucket_delivered_kwh.values()),
        "total_eb_price": sum(bucket_costs.values()),
    }


def _missing_inputs(inputs: DailyCalculationInput) -> list[str]:
    missing = []
    if inputs.consumption is None:
        missing.append("consumption")
    for market, data in inputs.markets.items():
        if data.purchased_mwh == 0 and data.iex_payout == 0:
            missing.append(f"{market}_market_data")
    return missing


def calculate_daily(
    inputs: DailyCalculationInput,
    mode: str,
    assumptions: CalculationAssumptions | None = None,
) -> DailyCalculationOutput:
    """Calculate one daily sheet output in parity or corrected mode."""
    assumptions = assumptions or CalculationAssumptions()
    parity_day = inputs.trading_date.day if mode == "parity" else None
    markets = {
        name: calculate_market_purchase(market, assumptions, parity_day=parity_day)
        for name, market in inputs.markets.items()
    }
    eb = calculate_equivalent_eb_price(inputs, assumptions)

    iex_price = sum(item["total_cost"] for item in markets.values())
    delivered = eb["total_delivered_kwh"]
    eb_price = eb["total_eb_price"]
    divide = parity_divide if mode == "parity" else safe_divide
    iex_price_per_unit = divide(iex_price, delivered)
    eb_price_per_unit = divide(eb_price, delivered)
    cost_saving = eb_price - iex_price
    active_losses = [
        market.ctu_loss_pct
        for market in inputs.markets.values()
        if market.purchased_mwh or market.iex_payout or any(market.bucket_mwh.values())
    ]
    line_loss_pct = active_losses[0] if active_losses else None
    unit_saving = (
        "#DIV/0!"
        if mode == "parity" and isinstance(iex_price_per_unit, str)
        else (
            None
            if not isinstance(iex_price_per_unit, (int, float)) or not isinstance(eb_price_per_unit, (int, float))
            else eb_price_per_unit - iex_price_per_unit
        )
    )

    return DailyCalculationOutput(
        trading_date=inputs.trading_date,
        day=inputs.trading_date.day,
        mode=mode,
        is_complete=not _missing_inputs(inputs),
        missing_inputs=_missing_inputs(inputs),
        b44_iex_price=iex_price,
        b45_iex_price_per_unit=iex_price_per_unit,
        b46_eb_price=eb_price,
        b47_eb_price_per_unit=eb_price_per_unit,
        cost_saving=cost_saving,
        cost_saving_per_unit=unit_saving,
        details={
            "calculation_version": CALCULATION_VERSION,
            "line_loss_pct": line_loss_pct,
            "markets": markets,
            "equivalent_eb": eb,
            "consumption": inputs.consumption.model_dump(mode="json") if inputs.consumption else None,
            "assumptions": assumptions.__dict__,
        },
    )


def _numeric_difference(left: Any, right: Any) -> float | None:
    if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
        return None
    return right - left


def compare_daily(
    inputs: DailyCalculationInput,
    assumptions: CalculationAssumptions | None = None,
) -> DailyComparisonOutput:
    """Return parity and corrected daily outputs with differences."""
    assumptions = assumptions or CalculationAssumptions()
    parity = calculate_daily(inputs, "parity", assumptions)
    corrected = calculate_daily(inputs, "corrected", assumptions)
    differences = {
        "b44_iex_price": _numeric_difference(parity.b44_iex_price, corrected.b44_iex_price),
        "b45_iex_price_per_unit": _numeric_difference(parity.b45_iex_price_per_unit, corrected.b45_iex_price_per_unit),
        "b46_eb_price": _numeric_difference(parity.b46_eb_price, corrected.b46_eb_price),
        "b47_eb_price_per_unit": _numeric_difference(parity.b47_eb_price_per_unit, corrected.b47_eb_price_per_unit),
        "cost_saving": _numeric_difference(parity.cost_saving, corrected.cost_saving),
        "cost_saving_per_unit": _numeric_difference(parity.cost_saving_per_unit, corrected.cost_saving_per_unit),
    }
    numeric_diffs = [abs(item) for item in differences.values() if item is not None]
    return DailyComparisonOutput(
        trading_date=inputs.trading_date,
        day=inputs.trading_date.day,
        parity=parity,
        corrected=corrected,
        differences=differences,
        within_tolerance=all(item <= assumptions.tolerance for item in numeric_diffs),
    )


def _output_number(value: Any) -> float | None:
    """Return API-safe numeric output for totals."""
    return value if isinstance(value, (int, float)) else None


def calculate_savings_sheet(
    comparisons: list[DailyComparisonOutput],
    *,
    use_corrected: bool = True,
) -> SavingsSheetOutput:
    """Build the monthly Savings Sheet equivalent from daily outputs."""
    rows: list[SavingsSheetRow] = []
    for comparison in comparisons:
        output = comparison.corrected if use_corrected else comparison.parity
        rows.append(
            SavingsSheetRow(
                trading_date=comparison.trading_date,
                day=comparison.day,
                line_loss_pct=output.details.get("line_loss_pct"),
                iex_price=output.b44_iex_price,
                equivalent_eb_price=output.b46_eb_price,
                total_cost_saving=output.cost_saving,
                iex_price_per_unit=output.b45_iex_price_per_unit,
                equivalent_eb_price_per_unit=output.b47_eb_price_per_unit,
                cost_saving_per_unit=output.cost_saving_per_unit,
                bill_for_exchange_purchase=output.b44_iex_price,
            )
        )

    iex_prices = [_output_number(row.iex_price) for row in rows]
    eb_prices = [_output_number(row.equivalent_eb_price) for row in rows]
    savings = [_output_number(row.total_cost_saving) for row in rows]
    iex_unit_prices = [_output_number(row.iex_price_per_unit) for row in rows]
    eb_unit_prices = [_output_number(row.equivalent_eb_price_per_unit) for row in rows]
    saving_unit_prices = [_output_number(row.cost_saving_per_unit) for row in rows]

    def clean_sum(values: list[float | None]) -> float:
        return sum(value for value in values if value is not None)

    def clean_average(values: list[float | None]) -> float | None:
        usable = [value for value in values if value is not None]
        return sum(usable) / len(usable) if usable else None

    return SavingsSheetOutput(
        rows=rows,
        totals={
            "iex_price": clean_sum(iex_prices),
            "equivalent_eb_price": clean_sum(eb_prices),
            "total_cost_saving": clean_sum(savings),
            "iex_price_per_unit_average": clean_average(iex_unit_prices),
            "equivalent_eb_price_per_unit_average": clean_average(eb_unit_prices),
            "cost_saving_per_unit_average": clean_average(saving_unit_prices),
            "bill_for_exchange_purchase": clean_sum(iex_prices),
        },
    )


def calculate_slot_wise_consolidate(inputs: list[DailyCalculationInput]) -> SlotWiseConsolidateOutput:
    """Build the Slot Wise Consolidate equivalent for C1, C2, C4, and C5."""
    rows: list[SlotWiseConsolidateRow] = []
    for bucket in BUCKETS:
        consumption_kwh = 0.0
        iex_delivered_kwh = 0.0
        for daily_input in inputs:
            if daily_input.consumption:
                consumption_kwh += numeric(getattr(daily_input.consumption, f"{bucket}_kwh"))
            for market in daily_input.markets.values():
                if any(market.bucket_mwh.values()):
                    purchased_mwh = numeric(market.bucket_mwh.get(bucket))
                else:
                    purchased_mwh = market.purchased_mwh if bucket == "c1" else 0.0
                delivery = calculate_delivery_after_losses(
                    purchased_mwh,
                    market.ctu_loss_pct,
                    CalculationAssumptions(),
                )
                iex_delivered_kwh += delivery["delivered_at_bus_kwh"]

        rows.append(
            SlotWiseConsolidateRow(
                slot=bucket.upper(),
                consumption_kwh=consumption_kwh,
                iex_delivered_kwh=iex_delivered_kwh,
                balance_kwh=consumption_kwh - iex_delivered_kwh,
            )
        )
    return SlotWiseConsolidateOutput(rows=rows)


def persist_daily_result(
    db: Session,
    portfolio_id: int,
    result: DailyCalculationOutput | DailyComparisonOutput,
) -> MonthlyCalculation:
    """Persist the new calculation output separately from legacy savings logic."""
    trading_date = result.trading_date
    calculation_data = result.model_dump(mode="json")
    if isinstance(result, DailyComparisonOutput):
        metrics_source = result.corrected
        calculation_type = f"{CALCULATION_VERSION}:compare"
    else:
        metrics_source = result
        calculation_type = f"{CALCULATION_VERSION}:{result.mode}"

    existing = db.query(MonthlyCalculation).filter(
        and_(
            MonthlyCalculation.portfolio_id == portfolio_id,
            MonthlyCalculation.calculation_date == trading_date,
            MonthlyCalculation.calculation_type == calculation_type,
        )
    ).first()
    values = {
        "portfolio_id": portfolio_id,
        "year": trading_date.year,
        "month": trading_date.month,
        "day": trading_date.day,
        "calculation_date": trading_date,
        "calculation_type": calculation_type,
        "calculation_data": calculation_data,
        "total_scheduled_mwh": sum(market.purchased_mwh for market in build_calculation_inputs(db, portfolio_id, trading_date).markets.values()),
        "total_cost": numeric(metrics_source.b44_iex_price),
        "net_profit_loss": numeric(metrics_source.cost_saving),
    }
    if existing:
        for key, value in values.items():
            setattr(existing, key, value)
        row = existing
    else:
        row = MonthlyCalculation(**values)
        db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _source_file_audit(db: Session, portfolio_id: int, dates: list[date]) -> list[dict[str, Any]]:
    """Return compact source-file lineage for persisted month summaries."""
    files = (
        db.query(DailyFile)
        .filter(
            DailyFile.portfolio_id == portfolio_id,
            DailyFile.trading_date.in_(dates),
        )
        .order_by(DailyFile.trading_date, DailyFile.report_type)
        .all()
    )
    return [
        {
            "id": file.id,
            "trading_date": file.trading_date.isoformat(),
            "report_type": file.report_type,
            "main_category": file.main_category,
            "sub_category": file.sub_category,
            "original_filename": file.original_filename,
            "transaction_count": len(file.transactions),
        }
        for file in files
    ]


def _consumption_audit(inputs: list[DailyCalculationInput]) -> list[dict[str, Any]]:
    """Return compact consumption lineage for persisted month summaries."""
    return [
        {
            "trading_date": item.trading_date.isoformat(),
            "present": item.consumption is not None,
            "source": item.consumption.source if item.consumption else None,
            "base_tariff_per_unit": item.consumption.base_tariff_per_unit if item.consumption else None,
        }
        for item in inputs
    ]


def persist_monthly_summary(
    db: Session,
    portfolio_id: int,
    year: int,
    month: int,
    mode: str,
) -> MonthlyCalculation:
    """Persist the month-level Excel-conversion summary and audit payload."""
    dates = month_dates(year, month)
    assumptions = CalculationAssumptions()
    daily_inputs = [build_calculation_inputs(db, portfolio_id, trading_date) for trading_date in dates]
    comparisons = [compare_daily(inputs, assumptions) for inputs in daily_inputs]
    use_corrected = mode != "parity"
    savings_sheet = calculate_savings_sheet(comparisons, use_corrected=use_corrected)
    slot_wise_consolidate = calculate_slot_wise_consolidate(daily_inputs)
    completed_days = sum(
        1
        for comparison in comparisons
        if (comparison.corrected if use_corrected else comparison.parity).is_complete
    )
    missing_input_count = sum(
        len((comparison.corrected if use_corrected else comparison.parity).missing_inputs)
        for comparison in comparisons
    )
    calculation_date = date(year, month, 1)
    calculation_type = f"{CALCULATION_VERSION}:monthly:{mode}"
    calculation_data = {
        "calculation_version": CALCULATION_VERSION,
        "calculation_mode": mode,
        "scope": "month",
        "year": year,
        "month": month,
        "assumptions": assumptions.__dict__,
        "audit": {
            "source_files": _source_file_audit(db, portfolio_id, dates),
            "consumption": _consumption_audit(daily_inputs),
        },
        "daily_results": [comparison.model_dump(mode="json") for comparison in comparisons],
        "savings_sheet": savings_sheet.model_dump(mode="json"),
        "slot_wise_consolidate": slot_wise_consolidate.model_dump(mode="json"),
        "completion": {
            "days_total": len(dates),
            "days_complete": completed_days,
            "missing_input_count": missing_input_count,
        },
    }

    existing = db.query(MonthlyCalculation).filter(
        and_(
            MonthlyCalculation.portfolio_id == portfolio_id,
            MonthlyCalculation.calculation_date == calculation_date,
            MonthlyCalculation.calculation_type == calculation_type,
        )
    ).first()
    values = {
        "portfolio_id": portfolio_id,
        "year": year,
        "month": month,
        "day": 0,
        "calculation_date": calculation_date,
        "calculation_type": calculation_type,
        "calculation_data": calculation_data,
        "total_scheduled_mwh": sum(
            sum(market.purchased_mwh for market in daily_input.markets.values())
            for daily_input in daily_inputs
        ),
        "total_cost": numeric(savings_sheet.totals.get("iex_price")),
        "net_profit_loss": numeric(savings_sheet.totals.get("total_cost_saving")),
    }
    if existing:
        for key, value in values.items():
            setattr(existing, key, value)
        row = existing
    else:
        row = MonthlyCalculation(**values)
        db.add(row)
    db.commit()
    db.refresh(row)
    return row


def run_calculation(
    db: Session,
    portfolio_id: int,
    year: int,
    month: int,
    mode: str = "compare",
    day: int | None = None,
) -> list[DailyCalculationOutput | DailyComparisonOutput]:
    """Run daily or monthly calculation and persist results."""
    results: list[DailyCalculationOutput | DailyComparisonOutput] = []
    for trading_date in month_dates(year, month, day):
        inputs = build_calculation_inputs(db, portfolio_id, trading_date)
        if mode == "compare":
            result: DailyCalculationOutput | DailyComparisonOutput = compare_daily(inputs)
        else:
            result = calculate_daily(inputs, mode)
        persist_daily_result(db, portfolio_id, result)
        results.append(result)
    if day is None:
        persist_monthly_summary(db, portfolio_id, year, month, mode)
    return results


def build_calculation_trace(
    db: Session,
    portfolio_id: int,
    year: int,
    month: int,
    day: int | None = None,
) -> dict[str, Any]:
    """Return the internal QA trace from uploaded data to calculated outputs."""
    dates = month_dates(year, month, day)
    assumptions = CalculationAssumptions()
    daily_inputs = [build_calculation_inputs(db, portfolio_id, trading_date) for trading_date in dates]
    comparisons = [compare_daily(inputs, assumptions) for inputs in daily_inputs]

    files = (
        db.query(DailyFile)
        .filter(
            DailyFile.portfolio_id == portfolio_id,
            DailyFile.trading_date.in_(dates),
        )
        .order_by(DailyFile.trading_date, DailyFile.report_type)
        .all()
    )
    energy_days = (
        db.query(EnergyScheduleDay)
        .join(EnergyScheduleMonth)
        .filter(
            EnergyScheduleMonth.portfolio_id == portfolio_id,
            EnergyScheduleDay.trading_date.in_(dates),
        )
        .order_by(EnergyScheduleDay.trading_date)
        .all()
    )

    return {
        "source_files": [
            {
                "id": file.id,
                "trading_date": file.trading_date.isoformat(),
                "delivery_date": file.delivery_date.isoformat() if file.delivery_date else None,
                "report_type": file.report_type,
                "main_category": file.main_category,
                "sub_category": file.sub_category,
                "original_filename": file.original_filename,
                "transaction_count": len(file.transactions),
            }
            for file in files
        ],
        "energy_schedule_days": [
            {
                "id": item.id,
                "trading_date": item.trading_date.isoformat(),
                "has_gdam_data": bool(item.has_gdam_data),
                "has_dam_data": bool(item.has_dam_data),
                "has_rtm_data": bool(item.has_rtm_data),
                "has_sch_data": bool(item.has_sch_data),
                "is_complete": bool(item.is_complete),
                "gdam_scheduled_quantity_mwh": item.gdam_scheduled_quantity_mwh,
                "dam_scheduled_quantity_mwh": item.dam_scheduled_quantity_mwh,
                "rtm_scheduled_quantity_mwh": item.rtm_scheduled_quantity_mwh,
                "total_scheduled_mwh": item.total_scheduled_mwh,
                "total_consumption_after_losses_mwh": item.total_consumption_after_losses_mwh,
                "ctu_losses_percent": item.ctu_losses_percent,
                "total_cost": item.total_cost,
            }
            for item in energy_days
        ],
        "consumption_inputs": [
            {
                "trading_date": inputs.trading_date.isoformat(),
                "present": inputs.consumption is not None,
                "source": inputs.consumption.source if inputs.consumption else None,
                "c1_kwh": inputs.consumption.c1_kwh if inputs.consumption else None,
                "c2_kwh": inputs.consumption.c2_kwh if inputs.consumption else None,
                "c4_kwh": inputs.consumption.c4_kwh if inputs.consumption else None,
                "c5_kwh": inputs.consumption.c5_kwh if inputs.consumption else None,
                "base_tariff_per_unit": inputs.consumption.base_tariff_per_unit if inputs.consumption else None,
            }
            for inputs in daily_inputs
        ],
        "daily_outputs": [
            {
                "trading_date": comparison.trading_date.isoformat(),
                "day": comparison.day,
                "is_complete": comparison.corrected.is_complete,
                "missing_inputs": comparison.corrected.missing_inputs,
                "b44_iex_price": comparison.corrected.b44_iex_price,
                "b45_iex_price_per_unit": comparison.corrected.b45_iex_price_per_unit,
                "b46_eb_price": comparison.corrected.b46_eb_price,
                "b47_eb_price_per_unit": comparison.corrected.b47_eb_price_per_unit,
                "cost_saving": comparison.corrected.cost_saving,
                "within_tolerance": comparison.within_tolerance,
            }
            for comparison in comparisons
        ],
        "savings_sheet": calculate_savings_sheet(comparisons).model_dump(mode="json"),
        "slot_wise_consolidate": calculate_slot_wise_consolidate(daily_inputs).model_dump(mode="json"),
    }
