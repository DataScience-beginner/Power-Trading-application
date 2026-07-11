"""
FastAPI Backend for Power Trading Application
Enterprise-level API with file upload and data retrieval
Version: 1.0.1
"""

import os
from pathlib import Path
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from api.routers import (
    admin,
    ai,
    ai_foundation,
    ai_insights,
    analytics,
    chat_auth,
    chatbot,
    clients,
    energy_calculations,
    energy_schedule,
    forecasting,
    health,
    reports,
    uploads,
    web,
    workbooks,
)
from database.config import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and optional mock data during application startup."""
    print("🗄️  Initializing database...")
    init_db()
    print("✅ Database ready")

    if os.getenv("AUTO_LOAD_MOCK_DATA", "false").lower() == "true":
        try:
            from database.config import SessionLocal
            from database.services import get_all_clients

            db = SessionLocal()
            try:
                clients = get_all_clients(db)
                if len(clients) == 0:
                    print("📊 Database is empty, loading mock data...")
                    import subprocess
                    subprocess.run([sys.executable, "scripts/data_generation/generate_mock_reports.py"], check=False)
                    subprocess.run([sys.executable, "scripts/ingestion/upload_mock_reports.py"], check=False)
                    subprocess.run([sys.executable, "scripts/energy_schedule/rebuild_energy_schedules.py"], check=False)
                    print("✅ Mock data loaded")
                else:
                    print(f"✅ Database has {len(clients)} clients already")
            finally:
                db.close()
        except Exception as e:
            print(f"⚠️  Mock data load failed: {e}")
            print("   You can upload files manually via the UI")
    else:
        print("ℹ️  AUTO_LOAD_MOCK_DATA is disabled")

    yield


app = FastAPI(
    title="Power Trading Data API",
    description="Enterprise API for parsing and managing power trading data",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files - check multiple possible locations
frontend_dir = Path(__file__).parent.parent / "frontend"
frontend_react_dist = Path(__file__).parent.parent / "frontend-react" / "dist"

if frontend_react_dist.exists():
    # Production: serve React build
    app.mount("/assets", StaticFiles(directory=str(frontend_react_dist / "assets")), name="assets")
elif frontend_dir.exists() and (frontend_dir / "static").exists():
    # Legacy: serve old frontend static files
    app.mount("/static", StaticFiles(directory=str(frontend_dir / "static")), name="static")

app.include_router(health.router)
app.include_router(clients.router)
app.include_router(analytics.router)
app.include_router(reports.router)
app.include_router(ai.router)
app.include_router(ai_foundation.router)
app.include_router(ai_insights.router)
app.include_router(chat_auth.router)
app.include_router(chatbot.router)
app.include_router(energy_calculations.router)
app.include_router(energy_schedule.router)
app.include_router(forecasting.router)
app.include_router(uploads.router)
app.include_router(workbooks.router)
app.include_router(admin.router)
app.include_router(web.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
