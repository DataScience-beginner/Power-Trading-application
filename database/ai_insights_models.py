"""AI-1 persistence for reproducible data-quality runs and findings."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text

from database.config import Base


def new_id() -> str:
    """Return a portable UUID identifier."""
    return str(uuid4())


def utc_now() -> datetime:
    """Return naive UTC to match existing application timestamps."""
    return datetime.now(UTC).replace(tzinfo=None)


class DataQualityRun(Base):
    """Reproducible execution of a versioned data-quality policy."""

    __tablename__ = "data_quality_runs"
    __table_args__ = (Index("ix_quality_run_scope", "client_id", "portfolio_id", "started_at"),)

    id = Column(String(36), primary_key=True, default=new_id)
    correlation_id = Column(String(100), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    policy_version = Column(String(40), nullable=False, default="data-quality-v1")
    policy_configuration = Column(JSON, nullable=False, default=dict)
    engine_version = Column(String(40), nullable=False, default="1.0.0")
    status = Column(String(30), nullable=False, default="completed")
    files_evaluated = Column(Integer, nullable=False, default=0)
    transactions_evaluated = Column(Integer, nullable=False, default=0)
    finding_counts = Column(JSON, nullable=False, default=dict)
    data_classification = Column(String(30), nullable=False, default="unknown")
    started_at = Column(DateTime, nullable=False, default=utc_now)
    completed_at = Column(DateTime, nullable=True, default=utc_now)


class DataQualityFinding(Base):
    """Evidence-backed finding produced by a deterministic quality rule."""

    __tablename__ = "data_quality_findings"
    __table_args__ = (Index("ix_quality_finding_scope", "client_id", "portfolio_id", "severity"),)

    id = Column(String(36), primary_key=True, default=new_id)
    run_id = Column(String(36), ForeignKey("data_quality_runs.id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True, index=True)
    daily_file_id = Column(Integer, ForeignKey("daily_files.id"), nullable=True, index=True)
    rule_id = Column(String(120), nullable=False, index=True)
    rule_version = Column(String(40), nullable=False, default="1.0.0")
    severity = Column(String(20), nullable=False, index=True)
    category = Column(String(60), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=False, default=list)
    recommended_action = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    status = Column(String(30), nullable=False, default="open")
    detected_at = Column(DateTime, nullable=False, default=utc_now)
