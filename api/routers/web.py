"""Web entrypoint routes for serving frontend pages."""

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


router = APIRouter(tags=["web"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
REACT_DIST_DIR = PROJECT_ROOT / "frontend-react" / "dist"


@router.get(
    "/",
    summary="Serve frontend or API root",
    description="Serves the React application when built, falls back to the legacy dashboard, or returns API discovery metadata.",
    response_model=None,
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
    response_model=None,
)
async def parser_ui() -> FileResponse | dict[str, str]:
    """Serve parser UI or a not-found message."""
    html_file = FRONTEND_DIR / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "Parser UI not found"}


@router.get(
    "/manifest.json",
    summary="Serve frontend manifest",
    description="Returns the React progressive-web-app manifest as JSON instead of the SPA fallback document.",
    response_model=None,
)
async def manifest() -> FileResponse | dict[str, str]:
    """Serve the manifest file directly so browser parsers receive JSON."""
    manifest_file = REACT_DIST_DIR / "manifest.json"
    if manifest_file.exists():
        return FileResponse(manifest_file, media_type="application/manifest+json")
    return {"message": "Frontend manifest not found"}


@router.get(
    "/vite.svg",
    summary="Serve frontend icon",
    description="Returns the frontend icon without routing it through the SPA fallback.",
    response_model=None,
)
async def vite_icon() -> FileResponse | dict[str, str]:
    """Serve the Vite icon when present in the public build directory."""
    icon_file = REACT_DIST_DIR / "vite.svg"
    if icon_file.exists():
        return FileResponse(icon_file, media_type="image/svg+xml")
    return {"message": "Frontend icon not found"}


@router.get(
    "/energy-schedule",
    summary="Serve energy schedule page",
    description="Serves the legacy energy schedule dashboard page when available.",
    response_model=None,
)
async def energy_schedule_page() -> FileResponse | dict[str, str]:
    """Serve energy schedule UI or a not-found message."""
    energy_schedule_file = FRONTEND_DIR / "energy_schedule.html"
    if energy_schedule_file.exists():
        return FileResponse(energy_schedule_file)
    return {"message": "Energy Schedule page not found"}


@router.get(
    "/{full_path:path}",
    summary="Serve React SPA fallback",
    description="Serves the React application for public SaaS and authenticated app routes on direct browser refresh.",
    response_model=None,
)
async def react_spa_fallback(full_path: str) -> FileResponse:
    """Serve React index.html for browser-managed routes."""
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")

    react_index = REACT_DIST_DIR / "index.html"
    if react_index.exists():
        return FileResponse(react_index)

    raise HTTPException(status_code=404, detail="React application build not found")
