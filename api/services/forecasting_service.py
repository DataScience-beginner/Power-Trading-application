"""Governed tenant-scoped solar forecast calibration, backtesting, and persistence."""

from datetime import date, timedelta
from statistics import median

from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.schemas.forecasting import ForecastPointResponse, SolarForecastRequest, SolarForecastResponse
from api.services.weather_service import WeatherService
from database.ai_foundation_models import AIExecutionAudit
from database.forecasting_models import ForecastPoint, ForecastRun, GenerationObservation
from database.models import Client, Portfolio


MODEL_NAME = "calibrated-physical-baseline"
MODEL_VERSION = "1.0.0"
CONTRACT_VERSION = "solar-forecast-v1"


def _portfolio_scope(db: Session, client_id: int, portfolio_id: int) -> tuple[Client, Portfolio]:
    client = db.query(Client).filter(Client.id == client_id).first()
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.client_id == client_id).first()
    if not client or not portfolio:
        raise HTTPException(status_code=404, detail="Client/portfolio scope not found")
    if client.lat is None or client.lon is None or not client.capacity_kw:
        raise HTTPException(status_code=422, detail="Client location and solar capacity must be configured")
    return client, portfolio


def _expected_kwh(capacity_kw: float, irradiation: float, temperature: float, factor: float) -> float:
    temperature_derate = max(0.75, 1 - max(0, temperature - 25) * 0.004)
    return max(0.0, capacity_kw * irradiation * factor * temperature_derate)


def _calibrate(observations: list[GenerationObservation], capacity_kw: float) -> tuple[float, dict[str, float | None]]:
    usable = [item for item in observations if item.irradiation_kwh_m2 and item.irradiation_kwh_m2 > 0]
    if not usable:
        return 0.78, {"mae_kwh": None, "mape_pct": None, "backtest_points": 0}
    training = usable[:-7] if len(usable) >= 14 else usable
    factors = [item.energy_kwh / (capacity_kw * item.irradiation_kwh_m2) for item in training]
    factor = min(0.95, max(0.45, median(factors)))
    holdout = usable[-7:] if len(usable) >= 14 else []
    if not holdout:
        return factor, {"mae_kwh": None, "mape_pct": None, "backtest_points": 0}
    errors = []
    percentage_errors = []
    for item in holdout:
        predicted = _expected_kwh(capacity_kw, item.irradiation_kwh_m2, item.temperature_c or 25, factor)
        errors.append(abs(predicted - item.energy_kwh))
        if item.energy_kwh > 0:
            percentage_errors.append(abs(predicted - item.energy_kwh) / item.energy_kwh * 100)
    return factor, {
        "mae_kwh": round(sum(errors) / len(errors), 2),
        "mape_pct": round(sum(percentage_errors) / len(percentage_errors), 2) if percentage_errors else None,
        "backtest_points": len(holdout),
    }


def run_solar_forecast(db: Session, actor_id: str, payload: SolarForecastRequest) -> SolarForecastResponse:
    """Run an auditable probabilistic baseline; never place bids or mutate schedules."""
    client, _ = _portfolio_scope(db, payload.client_id, payload.portfolio_id)
    portfolio_count = max(1, db.query(Portfolio).filter(Portfolio.client_id == client.id).count())
    capacity_kw = float(client.capacity_kw) / portfolio_count
    observations = db.query(GenerationObservation).filter(
        GenerationObservation.client_id == client.id,
        GenerationObservation.portfolio_id == payload.portfolio_id,
        GenerationObservation.quality_status == "accepted",
    ).order_by(GenerationObservation.observed_date).all()
    factor, metrics = _calibrate(observations, capacity_kw)
    weather, weather_source, limitations = WeatherService().daily_forecast(client.lat, client.lon, payload.horizon_days)
    if len(observations) < 14:
        limitations.append("Fewer than 14 generation observations are available; the default physical calibration is emphasized.")
    classification = "synthetic" if observations and all(item.is_synthetic for item in observations) else "actual" if observations else "unknown"
    confidence = 0.82 if metrics["backtest_points"] and weather_source == "actual_api" else 0.62 if observations else 0.4
    run = ForecastRun(
        correlation_id=payload.correlation_id,
        client_id=client.id,
        portfolio_id=payload.portfolio_id,
        contract_version=CONTRACT_VERSION,
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        weather_provider=WeatherService.provider,
        weather_source=weather_source,
        data_classification=classification,
        latitude=client.lat,
        longitude=client.lon,
        capacity_kw=capacity_kw,
        horizon_days=payload.horizon_days,
        training_points=len(observations),
        calibration_factor=factor,
        backtest_metrics=metrics,
        limitations=limitations,
        confidence=confidence,
    )
    db.add(run); db.flush()
    points = []
    for item in weather:
        p50 = _expected_kwh(capacity_kw, item["irradiation_kwh_m2"], item["temperature_c"], factor)
        uncertainty = 0.12 + min(0.18, item["cloud_cover_pct"] / 500)
        point = ForecastPoint(
            run_id=run.id,
            forecast_date=item["date"],
            p10_kwh=round(p50 * (1 - uncertainty), 2),
            p50_kwh=round(p50, 2),
            p90_kwh=round(p50 * (1 + uncertainty), 2),
            irradiation_kwh_m2=item["irradiation_kwh_m2"],
            temperature_c=item["temperature_c"],
            cloud_cover_pct=item["cloud_cover_pct"],
        )
        db.add(point); points.append(point)
    db.add(AIExecutionAudit(
        correlation_id=payload.correlation_id,
        client_id=client.id,
        portfolio_id=payload.portfolio_id,
        actor_type="user",
        actor_id=actor_id,
        agent_id="solar-forecast",
        agent_version="1.0.0",
        capability="forecast.solar.daily",
        contract_version=CONTRACT_VERSION,
        model_provider="innowatt",
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        input_references=[{"generation_observations": len(observations)}, {"weather_provider": WeatherService.provider}],
        tool_calls=[{"tool": "weather.daily_forecast", "source": weather_source}],
        output_payload={"forecast_run_id": run.id, "horizon_days": payload.horizon_days, "backtest": metrics},
        confidence=confidence,
        limitations=limitations,
    ))
    db.commit()
    return forecast_response(db, run)


def forecast_response(db: Session, run: ForecastRun) -> SolarForecastResponse:
    points = db.query(ForecastPoint).filter(ForecastPoint.run_id == run.id).order_by(ForecastPoint.forecast_date).all()
    return SolarForecastResponse(
        run_id=run.id,
        client_id=run.client_id,
        portfolio_id=run.portfolio_id,
        contract_version=run.contract_version,
        model_name=run.model_name,
        model_version=run.model_version,
        weather_provider=run.weather_provider,
        weather_source=run.weather_source,
        data_classification=run.data_classification,
        location={"latitude": run.latitude, "longitude": run.longitude},
        capacity_kw=run.capacity_kw,
        training_points=run.training_points,
        calibration_factor=run.calibration_factor,
        backtest_metrics=run.backtest_metrics,
        confidence=run.confidence,
        limitations=run.limitations,
        points=[ForecastPointResponse.model_validate(item, from_attributes=True) for item in points],
        created_at=run.created_at,
    )


def latest_solar_forecast(db: Session, client_id: int, portfolio_id: int) -> SolarForecastResponse:
    _portfolio_scope(db, client_id, portfolio_id)
    run = db.query(ForecastRun).filter(
        ForecastRun.client_id == client_id,
        ForecastRun.portfolio_id == portfolio_id,
    ).order_by(ForecastRun.created_at.desc()).first()
    if not run:
        raise HTTPException(status_code=404, detail="No solar forecast exists for this scope")
    return forecast_response(db, run)
