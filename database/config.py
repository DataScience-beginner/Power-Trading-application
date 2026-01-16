"""
Database Configuration for Power Trading Application

This file sets up the SQLite database connection using SQLAlchemy ORM.
SQLAlchemy is an Object-Relational Mapping (ORM) tool that lets us work with
database tables as Python classes instead of writing raw SQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database file path
DATABASE_DIR = os.path.join(os.path.dirname(__file__), '..')
DATABASE_FILE = os.path.join(DATABASE_DIR, 'power_trading.db')
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# Create engine
# echo=True will print all SQL statements (useful for learning/debugging)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite with FastAPI
    echo=False  # Set to True to see all SQL queries
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
