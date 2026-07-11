"""AI-2 persistence for solar observations, forecast runs, and forecast points."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, String, UniqueConstraint

from database.config import Base


def new_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class GenerationObservation(Base):
    """Daily metered or synthetic generation used for model calibration."""

    __tablename__ = "generation_observations"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "observed_date", "source_version", name="uq_generation_observation"),
        Index("ix_generation_scope_date", "client_id", "portfolio_id", "observed_date"),
    )

    id = Column(String(36), primary_key=True, default=new_id)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    observed_date = Column(Date, nullable=False, index=True)
    energy_kwh = Column(Float, nullable=False)
    irradiation_kwh_m2 = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    source_type = Column(String(40), nullable=False, default="meter")
    source_version = Column(String(40), nullable=False, default="generation-v1")
    is_synthetic = Column(Boolean, nullable=False, default=False)
    quality_status = Column(String(30), nullable=False, default="accepted")
    observation_metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=utc_now)


class ForecastRun(Base):
    """Versioned tenant-scoped model execution and backtest envelope."""

    __tablename__ = "forecast_runs"
    __table_args__ = (Index("ix_forecast_run_scope", "client_id", "portfolio_id", "created_at"),)

    id = Column(String(36), primary_key=True, default=new_id)
    correlation_id = Column(String(100), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    forecast_type = Column(String(40), nullable=False, default="solar_generation")
    contract_version = Column(String(40), nullable=False, default="solar-forecast-v1")
    model_name = Column(String(100), nullable=False, default="calibrated-physical-baseline")
    model_version = Column(String(40), nullable=False, default="1.0.0")
    weather_provider = Column(String(80), nullable=False)
    weather_source = Column(String(30), nullable=False)
    data_classification = Column(String(30), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity_kw = Column(Float, nullable=False)
    horizon_days = Column(Integer, nullable=False)
    training_points = Column(Integer, nullable=False, default=0)
    calibration_factor = Column(Float, nullable=False)
    backtest_metrics = Column(JSON, nullable=False, default=dict)
    limitations = Column(JSON, nullable=False, default=list)
    confidence = Column(Float, nullable=False)
    status = Column(String(30), nullable=False, default="completed")
    created_at = Column(DateTime, nullable=False, default=utc_now)


class ForecastPoint(Base):
    """Daily probabilistic output belonging to a forecast run."""

    __tablename__ = "forecast_points"
    __table_args__ = (UniqueConstraint("run_id", "forecast_date", name="uq_forecast_run_date"),)

    id = Column(String(36), primary_key=True, default=new_id)
    run_id = Column(String(36), ForeignKey("forecast_runs.id"), nullable=False, index=True)
    forecast_date = Column(Date, nullable=False, index=True)
    p10_kwh = Column(Float, nullable=False)
    p50_kwh = Column(Float, nullable=False)
    p90_kwh = Column(Float, nullable=False)
    irradiation_kwh_m2 = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=False)
    cloud_cover_pct = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utc_now)
