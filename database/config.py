"""
Database Configuration for Power Trading Application

Supports both SQLite (local development) and PostgreSQL (production).
DATABASE_URL environment variable determines which database to use.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load local environment files. Prefer .env.railway when present so local runs
# target the same Railway PostgreSQL instance as deployment.
project_root = Path(__file__).resolve().parent.parent
railway_env_file = project_root / ".env.railway"
default_env_file = project_root / ".env"

if railway_env_file.exists():
    load_dotenv(dotenv_path=railway_env_file, override=True)
elif default_env_file.exists():
    load_dotenv(dotenv_path=default_env_file)
else:
    load_dotenv()

# Get database URL from environment (Railway sets this for PostgreSQL)
# Falls back to SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL, check for Railway's individual PostgreSQL variables
if not DATABASE_URL:
    pg_host = os.getenv("PGHOST")
    pg_user = os.getenv("PGUSER", os.getenv("PGUSERNAME"))
    pg_password = os.getenv("PGPASSWORD")
    pg_database = os.getenv("PGDATABASE")
    pg_port = os.getenv("PGPORT", "5432")
    
    if all([pg_host, pg_user, pg_password, pg_database]):
        DATABASE_URL = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
    else:
        # Fallback to SQLite for local development
        DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'power_trading.db')}"

# Fix for Railway PostgreSQL URL (uses postgres:// instead of postgresql://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"🗄️  Database: {'PostgreSQL (Production)' if 'postgresql' in DATABASE_URL else 'SQLite (Development)'}")

# Create engine with appropriate settings
if "postgresql" in DATABASE_URL:
    # PostgreSQL settings
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        echo=False
    )
else:
    # SQLite settings
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

# SessionLocal: Each instance is a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our database models
Base = declarative_base()

def get_db():
    """
    Dependency function that creates a new database session for each request
    and closes it when done. This is used in FastAPI endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database by creating all tables.
    This reads all the model classes (Client, Portfolio, etc.) and creates tables.
    """
    from database.models import (
        Client,
        Portfolio,
        DailyFile,
        Transaction,
        MonthlyCalculation,
        WorkbookUploadRecord,
        WorkbookResultRow,
    )
    # Register additive AI-0 tables with SQLAlchemy metadata. Existing V0 tables
    # remain unchanged; production promotion should still use the reviewed SQL migration.
    from database import ai_foundation_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized successfully")
