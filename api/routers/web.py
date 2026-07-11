"""Web entrypoint routes for serving frontend pages."""

from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(tags=["web"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
REACT_DIST_DIR = PROJECT_ROOT / "frontend-react" / "dist"


@router.get(
    "/",
    summary="Serve frontend or API root",
    description="Serves the React application when built, falls back to the legacy dashboard, or returns API discovery metadata.",
)
async def root() -> FileResponse | dict[str, Any]:
    """Serve the main web app or return basic API metadata."""
    react_index = REACT_DIST_DIR / "index.html"
    if react_index.exists():
        return FileResponse(react_index)

    dashboard_file = FRONTEND_DIR / "dashboard.html"
    if dashboard_file.exists():
        return FileResponse(dashboard_file)

    return {
        "message": "Power Trading Analytics Dashboard",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "upload": "/api/upload",
            "analytics": "/api/analytics/summary",
            "docs": "/docs",
        },
    }


@router.get(
    "/parser",
    summary="Serve parser UI",
    description="Serves the legacy parser UI when available.",
)
async def parser_ui() -> FileResponse | dict[str, str]:
    """Serve parser UI or a not-found message."""
    html_file = FRONTEND_DIR / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "Parser UI not found"}


@router.get(
    "/energy-schedule",
    summary="Serve energy schedule page",
    description="Serves the legacy energy schedule dashboard page when available.",
)
async def energy_schedule_page() -> FileResponse | dict[str, str]:
    """Serve energy schedule UI or a not-found message."""
    energy_schedule_file = FRONTEND_DIR / "energy_schedule.html"
    if energy_schedule_file.exists():
        return FileResponse(energy_schedule_file)
    return {"message": "Energy Schedule page not found"}

