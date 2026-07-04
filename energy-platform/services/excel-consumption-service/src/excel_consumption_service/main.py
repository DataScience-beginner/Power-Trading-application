from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from excel_consumption_service.api.router import router
from excel_consumption_service.core.config import get_settings
from excel_consumption_service.db.bootstrap import seed_reference_data
from excel_consumption_service.db.session import SessionLocal, schema_is_ready


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Verify migrated schema presence and seed demo RBAC data on startup."""

    if not schema_is_ready():
        raise RuntimeError(
            "Database schema is not initialized. Run `alembic upgrade head` in "
            "`services/excel-consumption-service` before starting the service."
        )
    db = SessionLocal()
    try:
        seed_reference_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.service_name,
    version="0.1.0",
    description="Tenant-aware workbook ingestion and Solar Working calculation service.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
