from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from excel_consumption_service.core.config import get_settings


settings = get_settings()

if settings.database_url.startswith("sqlite:///./"):
    relative_path = settings.database_url.removeprefix("sqlite:///./")
    Path(relative_path).parent.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Provide one database session per request."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def schema_is_ready() -> bool:
    """Check whether the migrated schema is present before startup seeding runs."""

    return inspect(engine).has_table("tenants")
