"""AI-2 solar forecast, demo provisioning, and tenant isolation tests."""

import asyncio
from datetime import date, timedelta

import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.routers.analytics import get_analytics_summary
from api.routers.clients import get_clients
from api.schemas.forecasting import DemoProvisionRequest, SolarForecastRequest
from api.security.chat_auth import authorize_scope, hash_password
from api.services.demo_provisioning_service import provision_demo
from api.services.forecasting_service import run_solar_forecast
from api.services.weather_service import WeatherService
from database.chatbot_models import AppUser, UserPortfolioAccess
from database.config import Base
from database.forecasting_models import ForecastPoint, ForecastRun, GenerationObservation
from database.models import Client, Portfolio


@pytest.fixture()
def db(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "forecast-test-jwt-secret-longer-than-thirty-two")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_demo_provisioning_is_idempotent_and_creates_five_tenants(db) -> None:
    request = DemoProvisionRequest(default_password="DemoPassword#2026", days_of_history=14, portfolios_per_client=2)
    first = provision_demo(db, request)
    second = provision_demo(db, request)
    assert first.clients_total == 5
    assert db.query(Client).count() == 5
    assert db.query(Portfolio).count() == 10
    assert db.query(AppUser).filter(AppUser.role == "client_user").count() == 5
    assert db.query(GenerationObservation).count() == 140
    assert second.records_created["clients"] == 0
    assert second.records_created["portfolios"] == 0
    assert second.records_created["transactions"] == 0


def test_admin_lists_all_clients_while_client_lists_only_its_tenant(db) -> None:
    result = provision_demo(db, DemoProvisionRequest(default_password="DemoPassword#2026", days_of_history=14))
    admin = AppUser(email="admin@example.com", display_name="Admin", password_hash=hash_password("AdminPassword#2026"), role="platform_admin")
    client_user = db.query(AppUser).filter(AppUser.email == result.tenants[0].user_email).first()
    db.add(admin); db.commit()
    admin_clients = asyncio.run(get_clients(db=db, user=admin))
    tenant_clients = asyncio.run(get_clients(db=db, user=client_user))
    assert admin_clients.count == 5
    assert tenant_clients.count == 1
    assert tenant_clients.clients[0].id == client_user.client_id
    analytics = asyncio.run(get_analytics_summary(db=db, user=client_user))
    assert analytics.summary.total_transactions == 384


def test_portfolio_authorization_rejects_cross_tenant_scope(db) -> None:
    result = provision_demo(db, DemoProvisionRequest(default_password="DemoPassword#2026", days_of_history=14))
    user = db.query(AppUser).filter(AppUser.email == result.tenants[0].user_email).first()
    with pytest.raises(Exception) as error:
        authorize_scope(db, user, result.tenants[1].client_id, result.tenants[1].portfolio_ids[0])
    assert error.value.status_code == 403


def test_solar_forecast_calibrates_backtests_persists_and_audits(db, monkeypatch) -> None:
    result = provision_demo(db, DemoProvisionRequest(default_password="DemoPassword#2026", days_of_history=21))
    tenant = result.tenants[0]
    user = db.query(AppUser).filter(AppUser.email == tenant.user_email).first()
    start = date.today()
    weather = [
        {"date": start + timedelta(days=index), "irradiation_kwh_m2": 5.2, "temperature_c": 29.0, "cloud_cover_pct": 25.0}
        for index in range(7)
    ]
    monkeypatch.setattr(WeatherService, "daily_forecast", lambda self, lat, lon, days: (weather[:days], "actual_api", []))
    payload = SolarForecastRequest(
        client_id=tenant.client_id,
        portfolio_id=tenant.portfolio_ids[0],
        horizon_days=7,
        correlation_id="forecast-test-correlation",
    )
    authorize_scope(db, user, payload.client_id, payload.portfolio_id)
    forecast = run_solar_forecast(db, user.id, payload)
    assert forecast.training_points == 21
    assert forecast.backtest_metrics["backtest_points"] == 7
    assert 0 < forecast.backtest_metrics["mape_pct"] < 20
    assert len(forecast.points) == 7
    assert all(point.p10_kwh < point.p50_kwh < point.p90_kwh for point in forecast.points)
    assert db.query(ForecastRun).count() == 1
    assert db.query(ForecastPoint).count() == 7


def test_weather_failure_is_explicitly_synthetic(monkeypatch) -> None:
    class FailedResponse:
        def raise_for_status(self):
            raise requests.RequestException("provider unavailable")

    monkeypatch.setattr("requests.get", lambda *args, **kwargs: FailedResponse())
    rows, source, limitations = WeatherService().daily_forecast(12.97, 80.22, 3)
    assert len(rows) == 3
    assert source == "synthetic_fallback"
    assert limitations


def test_forecast_migration_is_additive() -> None:
    migration = open("database/migrations/forecasting_v1.sql", encoding="utf-8").read().upper()
    for table in ["GENERATION_OBSERVATIONS", "FORECAST_RUNS", "FORECAST_POINTS"]:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in migration
    assert "DROP TABLE" not in migration
