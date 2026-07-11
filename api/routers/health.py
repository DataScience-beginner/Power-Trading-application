"""Health and platform status routes."""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(tags=["health"])


class HealthCheckResponse(BaseModel):
    """Response returned by the API health endpoint."""

    status: str = Field(..., description="Current API status.")
    timestamp: str = Field(..., description="Server timestamp in ISO-8601 format.")
    service: str = Field(..., description="Service name.")


@router.get(
    "/api/health",
    response_model=HealthCheckResponse,
    summary="Check API health",
    description="Returns a lightweight health response for deployments, monitors, agents, and chatbots.",
)
async def health_check() -> HealthCheckResponse:
    """Return API health status without touching the database."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        service="Power Trading API",
    )

