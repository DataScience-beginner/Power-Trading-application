"""Typed AI-2 solar forecasting and demo provisioning contracts."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class SolarForecastRequest(BaseModel):
    client_id: int = Field(..., gt=0, description="Authorized tenant identifier.")
    portfolio_id: int = Field(..., gt=0, description="Authorized portfolio containing the solar asset.")
    horizon_days: int = Field(7, ge=1, le=14, description="Daily forecast horizon.")
    correlation_id: str = Field(..., min_length=8, max_length=100)


class ForecastPointResponse(BaseModel):
    forecast_date: date
    p10_kwh: float
    p50_kwh: float
    p90_kwh: float
    irradiation_kwh_m2: float
    temperature_c: float
    cloud_cover_pct: float


class SolarForecastResponse(BaseModel):
    run_id: str
    client_id: int
    portfolio_id: int
    contract_version: str
    model_name: str
    model_version: str
    weather_provider: str
    weather_source: str
    data_classification: str
    location: dict[str, float]
    capacity_kw: float
    training_points: int
    calibration_factor: float
    backtest_metrics: dict[str, float | None]
    confidence: float
    limitations: list[str]
    human_review_required: bool = True
    points: list[ForecastPointResponse]
    created_at: datetime


class DemoProvisionRequest(BaseModel):
    default_password: str = Field(..., min_length=12, max_length=200)
    days_of_history: int = Field(30, ge=14, le=90)
    portfolios_per_client: int = Field(2, ge=2, le=4)


class DemoTenantResponse(BaseModel):
    client_id: int
    entity_id: str
    entity_name: str
    portfolio_ids: list[int]
    portfolio_codes: list[str]
    user_email: str


class DemoProvisionResponse(BaseModel):
    status: str
    data_classification: str
    clients_total: int
    tenants: list[DemoTenantResponse]
    records_created: dict[str, int]
    note: str
