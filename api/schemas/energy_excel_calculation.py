"""Schemas for Excel-parity energy schedule calculations."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


CalculationMode = Literal["parity", "corrected", "compare"]


class ConsumptionEntry(BaseModel):
    portfolio_id: int
    consumption_date: date
    c1_kwh: float = 0.0
    c2_kwh: float = 0.0
    c4_kwh: float = 0.0
    c5_kwh: float = 0.0
    base_tariff_per_unit: float | None = None
    source: str = "manual"
    notes: str | None = None


class ConsumptionSaveRequest(BaseModel):
    records: list[ConsumptionEntry] = Field(min_length=1)


class ConsumptionResponse(BaseModel):
    success: bool
    count: int
    records: list[ConsumptionEntry]


class CalculationRunRequest(BaseModel):
    portfolio_id: int | None = None
    year: int | None = None
    month: int | None = Field(default=None, ge=1, le=12)
    day: int | None = Field(default=None, ge=1, le=31)
    calculation_date: date | None = None
    mode: CalculationMode = "compare"


class DailyCalculationOutput(BaseModel):
    trading_date: date
    day: int
    mode: str
    is_complete: bool
    missing_inputs: list[str]
    b44_iex_price: float | str | None
    b45_iex_price_per_unit: float | str | None
    b46_eb_price: float | str | None
    b47_eb_price_per_unit: float | str | None
    cost_saving: float | str | None
    cost_saving_per_unit: float | str | None
    details: dict[str, Any] = Field(default_factory=dict)


class DailyComparisonOutput(BaseModel):
    trading_date: date
    day: int
    parity: DailyCalculationOutput
    corrected: DailyCalculationOutput
    differences: dict[str, float | None]
    within_tolerance: bool


class SavingsSheetRow(BaseModel):
    trading_date: date
    day: int
    line_loss_pct: float | None
    iex_price: float | str | None
    equivalent_eb_price: float | str | None
    total_cost_saving: float | str | None
    iex_price_per_unit: float | str | None
    equivalent_eb_price_per_unit: float | str | None
    cost_saving_per_unit: float | str | None
    bill_for_exchange_purchase: float | str | None = None


class SavingsSheetOutput(BaseModel):
    rows: list[SavingsSheetRow]
    totals: dict[str, float | str | None]


class SlotWiseConsolidateRow(BaseModel):
    slot: str
    consumption_kwh: float
    iex_delivered_kwh: float
    balance_kwh: float


class SlotWiseConsolidateOutput(BaseModel):
    rows: list[SlotWiseConsolidateRow]


class CalculationRunResponse(BaseModel):
    success: bool
    mode: CalculationMode
    portfolio_id: int
    year: int
    month: int
    day: int | None = None
    days_processed: int
    results: list[DailyCalculationOutput | DailyComparisonOutput]


class ComparisonResponse(BaseModel):
    success: bool
    portfolio_id: int
    year: int
    month: int
    count: int
    tolerance: float
    comparisons: list[DailyComparisonOutput]
    savings_sheet: SavingsSheetOutput
    slot_wise_consolidate: SlotWiseConsolidateOutput


class CalculationTraceResponse(BaseModel):
    success: bool
    portfolio_id: int
    year: int
    month: int
    day: int | None = None
    count: int
    trace: dict[str, Any]


class SavedCalculationRow(BaseModel):
    id: int
    calculation_date: date
    day: int
    calculation_type: str | None = None
    calculated_at: datetime | None = None
    updated_at: datetime | None = None
    total_scheduled_mwh: float = 0.0
    total_cost: float = 0.0
    net_profit_loss: float = 0.0
    calculation_data: dict[str, Any] | None = None


class SavedCalculationResultsResponse(BaseModel):
    success: bool
    portfolio_id: int
    year: int
    month: int
    mode: CalculationMode
    day: int | None = None
    count: int
    latest_calculated_at: datetime | None = None
    monthly_summary: SavedCalculationRow | None = None
    results: list[SavedCalculationRow]
