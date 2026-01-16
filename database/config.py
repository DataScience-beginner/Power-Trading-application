"""
Database Configuration for Power Trading Application

Supports both SQLite (local development) and PostgreSQL (production).
DATABASE_URL environment variable determines which database to use.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment (Railway sets this for PostgreSQL)
# Falls back to SQLite for local development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'power_trading.db')}"
)

# Fix for Railway PostgreSQL URL (uses postgres:// instead of postgresql://)
if DATABASE_URL.startswith("postgres://"):
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
    from database.models import Client, Portfolio, DailyFile, Transaction, MonthlyCalculation
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized: {DATABASE_FILE}")
