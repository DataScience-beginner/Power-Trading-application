"""Authenticated AI-2 solar forecasting and demo provisioning routes."""

import os

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.schemas.forecasting import DemoProvisionRequest, DemoProvisionResponse, SolarForecastRequest, SolarForecastResponse
from api.security.chat_auth import authorize_scope, get_current_user, require_admin
from api.services.demo_provisioning_service import provision_demo
from api.services.forecasting_service import latest_solar_forecast, run_solar_forecast
from database.chatbot_models import AppUser
from database.config import get_db


router = APIRouter(prefix="/api/v1", tags=["ai-forecasting"])


@router.post(
    "/forecasts/solar/run",
    response_model=SolarForecastResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run solar generation forecast",
    description="Runs a tenant-scoped calibrated physical baseline with weather inputs, quantiles, backtest metrics, lineage, and audit.",
)
async def create_solar_forecast(
    payload: SolarForecastRequest,
    db: Session = Depends(get_db),
    user: AppUser = Depends(get_current_user),
) -> SolarForecastResponse:
    authorize_scope(db, user, payload.client_id, payload.portfolio_id)
    return run_solar_forecast(db, user.id, payload)


@router.get(
    "/forecasts/solar/latest",
    response_model=SolarForecastResponse,
    summary="Read latest solar generation forecast",
    description="Returns the latest persisted forecast only when JWT tenant and portfolio authorization succeeds.",
)
async def read_latest_solar_forecast(
    client_id: int,
    portfolio_id: int,
    db: Session = Depends(get_db),
    user: AppUser = Depends(get_current_user),
) -> SolarForecastResponse:
    authorize_scope(db, user, client_id, portfolio_id)
    return latest_solar_forecast(db, client_id, portfolio_id)


@router.post(
    "/admin/demo/provision",
    response_model=DemoProvisionResponse,
    summary="Provision five synthetic demo tenants",
    description="Idempotently creates five clients, multiple portfolios, scoped users, generation history, and compact trading fixtures.",
)
async def provision_multi_tenant_demo(
    payload: DemoProvisionRequest,
    db: Session = Depends(get_db),
    _admin: AppUser = Depends(require_admin),
) -> DemoProvisionResponse:
    if os.getenv("ENABLE_DEMO_PROVISIONING", "false").lower() != "true":
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Demo provisioning is disabled")
    return provision_demo(db, payload)
