"""AI-0 services for dynamic contracts, lineage, effective rules, and decisions."""

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.schemas.ai_foundation import (
    AIExecutionAuditCreate,
    BusinessRuleCreate,
    CanonicalEntityCreate,
    DecisionRecordCreate,
    ProcessingRunCreate,
    SourceArtifactCreate,
)
from database.ai_foundation_models import (
    AIExecutionAudit,
    BusinessRuleVersion,
    CanonicalEntity,
    DecisionRecord,
    ProcessingRun,
    SourceArtifact,
)
from database.models import Client, Portfolio


def validate_scope(db: Session, client_id: int, portfolio_id: int | None) -> None:
    """Ensure the requested portfolio belongs to the required client scope."""
    if not db.query(Client.id).filter(Client.id == client_id).first():
        raise HTTPException(status_code=404, detail="Client scope not found")
    if portfolio_id is not None:
        exists = db.query(Portfolio.id).filter(
            Portfolio.id == portfolio_id,
            Portfolio.client_id == client_id,
        ).first()
        if not exists:
            raise HTTPException(status_code=404, detail="Portfolio is not within the client scope")


def persist(db: Session, record):
    """Persist a record and convert uniqueness violations into stable API errors."""
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Version or idempotency key already exists") from exc


def create_canonical_entity(db: Session, payload: CanonicalEntityCreate) -> CanonicalEntity:
    """Persist a flexible canonical entity after tenant-scope validation."""
    validate_scope(db, payload.client_id, payload.portfolio_id)
    if payload.parent_entity_id:
        parent = db.query(CanonicalEntity).filter(
            CanonicalEntity.id == payload.parent_entity_id,
            CanonicalEntity.client_id == payload.client_id,
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent entity not found in client scope")
    return persist(db, CanonicalEntity(**payload.model_dump()))


def create_source_artifact(db: Session, payload: SourceArtifactCreate) -> SourceArtifact:
    """Register immutable source metadata; never store credentials in storage_uri."""
    validate_scope(db, payload.client_id, payload.portfolio_id)
    if payload.canonical_entity_id:
        entity = db.query(CanonicalEntity).filter(
            CanonicalEntity.id == payload.canonical_entity_id,
            CanonicalEntity.client_id == payload.client_id,
        ).first()
        if not entity:
            raise HTTPException(status_code=404, detail="Canonical entity not found in client scope")
    if payload.supersedes_artifact_id:
        previous = db.query(SourceArtifact).filter(
            SourceArtifact.id == payload.supersedes_artifact_id,
            SourceArtifact.client_id == payload.client_id,
        ).first()
        if not previous:
            raise HTTPException(status_code=404, detail="Superseded artifact not found in client scope")
    return persist(db, SourceArtifact(**payload.model_dump()))


def create_processing_run(db: Session, payload: ProcessingRunCreate) -> ProcessingRun:
    """Record a bounded processing execution against a scoped source artifact."""
    validate_scope(db, payload.client_id, payload.portfolio_id)
    artifact = db.query(SourceArtifact).filter(
        SourceArtifact.id == payload.source_artifact_id,
        SourceArtifact.client_id == payload.client_id,
    ).first()
    if not artifact or artifact.portfolio_id != payload.portfolio_id:
        raise HTTPException(status_code=404, detail="Source artifact not found in requested scope")
    return persist(db, ProcessingRun(**payload.model_dump()))


def create_business_rule(db: Session, payload: BusinessRuleCreate) -> BusinessRuleVersion:
    """Persist an effective-dated rule without changing source-code enums or columns."""
    return persist(db, BusinessRuleVersion(**payload.model_dump()))


def list_effective_rules(
    db: Session,
    rule_key: str | None,
    scope_type: str | None,
    scope_key: str | None,
    effective_at: datetime,
) -> list[BusinessRuleVersion]:
    """Return approved/active rule versions effective at a requested instant."""
    query = db.query(BusinessRuleVersion).filter(
        BusinessRuleVersion.status.in_(["approved", "active"]),
        BusinessRuleVersion.valid_from <= effective_at,
        or_(BusinessRuleVersion.valid_to.is_(None), BusinessRuleVersion.valid_to > effective_at),
    )
    if rule_key:
        query = query.filter(BusinessRuleVersion.rule_key == rule_key)
    if scope_type:
        query = query.filter(BusinessRuleVersion.scope_type == scope_type)
    if scope_key:
        query = query.filter(BusinessRuleVersion.scope_key == scope_key)
    return query.order_by(BusinessRuleVersion.rule_key, BusinessRuleVersion.version.desc()).all()


def create_audit_event(db: Session, payload: AIExecutionAuditCreate) -> AIExecutionAudit:
    """Persist an evidence envelope without storing hidden model reasoning."""
    validate_scope(db, payload.client_id, payload.portfolio_id)
    return persist(db, AIExecutionAudit(**payload.model_dump()))


def build_human_narrative(record: DecisionRecord) -> str:
    """Generate deterministic NLP from structured facts, not hidden model reasoning."""
    confidence = "not scored" if record.confidence is None else f"{record.confidence:.0%}"
    rationale = "; ".join(record.rationale or [])
    limitations = "; ".join(record.limitations or []) or "none recorded"
    review = "Human review is required." if record.human_review_required else "Human review is optional."
    return (
        f"{record.title}. {record.summary} "
        f"Rationale: {rationale}. Confidence: {confidence}. "
        f"Limitations: {limitations}. {review}"
    )


def create_decision(db: Session, payload: DecisionRecordCreate) -> DecisionRecord:
    """Persist a structured, evidence-backed decision within a validated scope."""
    validate_scope(db, payload.client_id, payload.portfolio_id)
    if payload.audit_event_id:
        audit = db.query(AIExecutionAudit).filter(
            AIExecutionAudit.id == payload.audit_event_id,
            AIExecutionAudit.client_id == payload.client_id,
        ).first()
        if not audit or audit.portfolio_id != payload.portfolio_id:
            raise HTTPException(status_code=404, detail="Audit event not found in requested scope")
    values = payload.model_dump()
    values["evidence"] = [item.model_dump(mode="json") for item in payload.evidence]
    return persist(db, DecisionRecord(**values))


def get_decision(db: Session, decision_id: str, client_id: int) -> DecisionRecord:
    """Retrieve a decision only through its required client scope."""
    record = db.query(DecisionRecord).filter(
        DecisionRecord.id == decision_id,
        DecisionRecord.client_id == client_id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Decision not found in client scope")
    return record
