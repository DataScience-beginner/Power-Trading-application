"""Additive AI-0 persistence models for lineage, rules, audits, and decisions.

These tables do not replace the first-cut trading schema. They provide a
versioned compatibility layer that can evolve while existing dashboards keep
using the current Client, Portfolio, DailyFile, and Transaction tables.
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from database.config import Base


def new_id() -> str:
    """Return a portable UUID string suitable for PostgreSQL and test SQLite."""
    return str(uuid4())


def utc_now() -> datetime:
    """Return naive UTC for compatibility with the existing timestamp columns."""
    return datetime.now(UTC).replace(tzinfo=None)


class CanonicalEntity(Base):
    """Versioned, extensible business entity mapped to today's client model."""

    __tablename__ = "canonical_entities"
    __table_args__ = (
        UniqueConstraint("entity_type", "external_key", "version", name="uq_canonical_entity_version"),
        Index("ix_canonical_entity_scope", "client_id", "portfolio_id", "entity_type"),
    )

    id = Column(String(36), primary_key=True, default=new_id)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True, index=True)
    parent_entity_id = Column(String(36), ForeignKey("canonical_entities.id"), nullable=True)
    entity_type = Column(String(80), nullable=False, index=True)
    external_key = Column(String(180), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    schema_version = Column(String(40), nullable=False, default="canonical-v1")
    version = Column(Integer, nullable=False, default=1)
    attributes = Column(JSON, nullable=False, default=dict)
    valid_from = Column(DateTime, nullable=False, default=utc_now)
    valid_to = Column(DateTime, nullable=True)
    status = Column(String(30), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, default=utc_now)

    parent = relationship("CanonicalEntity", remote_side=[id])


class SourceArtifact(Base):
    """Immutable metadata and lineage for a file, API payload, email, or meter feed."""

    __tablename__ = "source_artifacts"
    __table_args__ = (
        UniqueConstraint("client_id", "content_checksum", "artifact_version", name="uq_source_artifact_version"),
        Index("ix_source_artifact_scope", "client_id", "portfolio_id", "source_type"),
    )

    id = Column(String(36), primary_key=True, default=new_id)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True, index=True)
    canonical_entity_id = Column(String(36), ForeignKey("canonical_entities.id"), nullable=True)
    supersedes_artifact_id = Column(String(36), ForeignKey("source_artifacts.id"), nullable=True)
    source_type = Column(String(80), nullable=False, index=True)
    original_name = Column(String(500), nullable=False)
    content_checksum = Column(String(128), nullable=False, index=True)
    storage_uri = Column(String(1000), nullable=True)
    source_schema_version = Column(String(80), nullable=False, default="unknown")
    parser_name = Column(String(120), nullable=True)
    parser_version = Column(String(40), nullable=True)
    artifact_version = Column(Integer, nullable=False, default=1)
    status = Column(String(30), nullable=False, default="registered")
    is_synthetic = Column(Boolean, nullable=False, default=False)
    artifact_metadata = Column(JSON, nullable=False, default=dict)
    observed_at = Column(DateTime, nullable=True)
    registered_at = Column(DateTime, nullable=False, default=utc_now)

    processing_runs = relationship("ProcessingRun", back_populates="source_artifact")


class ProcessingRun(Base):
    """Auditable execution of classification, parsing, validation, or normalization."""

    __tablename__ = "processing_runs"
    __table_args__ = (Index("ix_processing_run_scope", "client_id", "portfolio_id", "run_type"),)

    id = Column(String(36), primary_key=True, default=new_id)
    correlation_id = Column(String(100), nullable=False, index=True)
    source_artifact_id = Column(String(36), ForeignKey("source_artifacts.id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True, index=True)
    run_type = Column(String(80), nullable=False, index=True)
    executor_type = Column(String(30), nullable=False, default="agent")
    executor_id = Column(String(120), nullable=False)
    executor_version = Column(String(40), nullable=False)
    contract_version = Column(String(40), nullable=False, default="ai-foundation-v1")
    status = Column(String(30), nullable=False, default="started")
    input_summary = Column(JSON, nullable=False, default=dict)
    output_summary = Column(JSON, nullable=False, default=dict)
    error_details = Column(JSON, nullable=False, default=dict)
    started_at = Column(DateTime, nullable=False, default=utc_now)
    completed_at = Column(DateTime, nullable=True)

    source_artifact = relationship("SourceArtifact", back_populates="processing_runs")


class BusinessRuleVersion(Base):
    """Effective-dated configuration for tariffs, markets, assets, and constraints."""

    __tablename__ = "business_rule_versions"
    __table_args__ = (
        UniqueConstraint("rule_key", "scope_type", "scope_key", "version", name="uq_business_rule_version"),
        Index("ix_business_rule_effective", "rule_key", "status", "valid_from", "valid_to"),
    )

    id = Column(String(36), primary_key=True, default=new_id)
    rule_key = Column(String(160), nullable=False, index=True)
    rule_type = Column(String(80), nullable=False, index=True)
    scope_type = Column(String(40), nullable=False, default="global")
    scope_key = Column(String(160), nullable=False, default="global")
    jurisdiction = Column(String(80), nullable=True)
    version = Column(Integer, nullable=False)
    schema_version = Column(String(40), nullable=False, default="rule-v1")
    configuration = Column(JSON, nullable=False, default=dict)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=True)
    status = Column(String(30), nullable=False, default="draft")
    approved_by = Column(String(120), nullable=True)
    approval_note = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)


class AIExecutionAudit(Base):
    """Immutable evidence envelope for an AI/agent execution."""

    __tablename__ = "ai_execution_audits"
    __table_args__ = (Index("ix_ai_audit_scope", "client_id", "portfolio_id", "capability"),)

    id = Column(String(36), primary_key=True, default=new_id)
    correlation_id = Column(String(100), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True, index=True)
    actor_type = Column(String(30), nullable=False)
    actor_id = Column(String(120), nullable=False)
    agent_id = Column(String(120), nullable=True)
    agent_version = Column(String(40), nullable=True)
    capability = Column(String(120), nullable=False, index=True)
    contract_version = Column(String(40), nullable=False, default="ai-foundation-v1")
    model_provider = Column(String(80), nullable=True)
    model_name = Column(String(120), nullable=True)
    model_version = Column(String(80), nullable=True)
    prompt_version = Column(String(80), nullable=True)
    input_references = Column(JSON, nullable=False, default=list)
    tool_calls = Column(JSON, nullable=False, default=list)
    output_payload = Column(JSON, nullable=False, default=dict)
    confidence = Column(Float, nullable=True)
    status = Column(String(30), nullable=False, default="completed")
    limitations = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, nullable=False, default=utc_now)

    decisions = relationship("DecisionRecord", back_populates="audit_event")


class DecisionRecord(Base):
    """Human- and agent-readable record of a recommendation or operational decision."""

    __tablename__ = "decision_records"
    __table_args__ = (Index("ix_decision_scope", "client_id", "portfolio_id", "decision_type"),)

    id = Column(String(36), primary_key=True, default=new_id)
    audit_event_id = Column(String(36), ForeignKey("ai_execution_audits.id"), nullable=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True, index=True)
    decision_type = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    rationale = Column(JSON, nullable=False, default=list)
    evidence = Column(JSON, nullable=False, default=list)
    alternatives = Column(JSON, nullable=False, default=list)
    limitations = Column(JSON, nullable=False, default=list)
    confidence = Column(Float, nullable=True)
    status = Column(String(30), nullable=False, default="proposed")
    human_review_required = Column(Boolean, nullable=False, default=True)
    reviewed_by = Column(String(120), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_note = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)

    audit_event = relationship("AIExecutionAudit", back_populates="decisions")
