"""AI-0 trust-foundation routes for agents, specialists, and future AI products."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from api.schemas.ai_foundation import (
    AIExecutionAuditCreate,
    AIExecutionAuditResponse,
    BusinessRuleCreate,
    BusinessRuleResponse,
    CanonicalEntityCreate,
    CanonicalEntityResponse,
    CapabilityCatalogResponse,
    CapabilityDefinition,
    DecisionRecordCreate,
    DecisionRecordResponse,
    ProcessingRunCreate,
    ProcessingRunResponse,
    SourceArtifactCreate,
    SourceArtifactResponse,
)
from api.services.ai_foundation_service import (
    build_human_narrative,
    create_audit_event,
    create_business_rule,
    create_canonical_entity,
    create_decision,
    create_processing_run,
    create_source_artifact,
    get_decision,
    list_effective_rules,
)
from api.security.ai_foundation import require_ai_foundation_access
from database.config import get_db


router = APIRouter(prefix="/api/v1/ai-foundation", tags=["ai-foundation"])


def utc_now() -> datetime:
    """Return naive UTC to match effective-dated database rules."""
    return datetime.now(UTC).replace(tzinfo=None)


CAPABILITIES = [
    CapabilityDefinition(capability_id="discover", purpose="Discover governed AI-0 contracts.", endpoint="/api/v1/ai-foundation/capabilities", method="GET", safety="read_only", writes_data=False, human_review="none"),
    CapabilityDefinition(capability_id="canonical-entity.register", purpose="Register a versioned flexible business entity.", endpoint="/api/v1/ai-foundation/entities", method="POST", safety="controlled_write", writes_data=True, human_review="required for authoritative mappings"),
    CapabilityDefinition(capability_id="source.register", purpose="Register immutable source lineage and synthetic-data status.", endpoint="/api/v1/ai-foundation/source-artifacts", method="POST", safety="controlled_write", writes_data=True, human_review="exception based"),
    CapabilityDefinition(capability_id="processing.record", purpose="Record a classification, parse, validation, or normalization run.", endpoint="/api/v1/ai-foundation/processing-runs", method="POST", safety="controlled_write", writes_data=True, human_review="failed and low-confidence runs"),
    CapabilityDefinition(capability_id="rule.version", purpose="Create an effective-dated business-rule version.", endpoint="/api/v1/ai-foundation/rules", method="POST", safety="controlled_write", writes_data=True, human_review="required before approval/activation"),
    CapabilityDefinition(capability_id="rule.resolve", purpose="Read effective approved rules at a historical or future instant.", endpoint="/api/v1/ai-foundation/rules/effective", method="GET", safety="read_only", writes_data=False, human_review="none"),
    CapabilityDefinition(capability_id="audit.record", purpose="Record evidence, model/tool versions, confidence, and limitations.", endpoint="/api/v1/ai-foundation/audit-events", method="POST", safety="controlled_write", writes_data=True, human_review="policy dependent"),
    CapabilityDefinition(capability_id="decision.record", purpose="Store an evidence-backed decision and human narrative.", endpoint="/api/v1/ai-foundation/decisions", method="POST", safety="controlled_write", writes_data=True, human_review="required by default"),
]


@router.get(
    "/capabilities",
    response_model=CapabilityCatalogResponse,
    summary="Discover AI foundation capabilities",
    description="Returns agent-readable capability, safety, review, and version metadata for AI Phase 0.",
)
async def get_capabilities() -> CapabilityCatalogResponse:
    """Return the governed AI-0 capability catalog without accessing client data."""
    return CapabilityCatalogResponse(
        foundation_version="v1",
        canonical_schema_status="evolving compatibility layer; not final domain model",
        mock_data_status="synthetic-v0 baseline; never treated as production truth",
        principles=[
            "Existing V0 tables remain backward compatible.",
            "Dynamic attributes and effective-dated rules evolve without hardcoded enums.",
            "Every write requires explicit client scope and produces traceable records.",
            "Generative text explains structured evidence; it does not become authoritative truth.",
        ],
        capabilities=CAPABILITIES,
    )


@router.post(
    "/entities",
    response_model=CanonicalEntityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register canonical entity",
    description="Registers a versioned site, meter, asset, contract, account, or future entity without altering the V0 schema.",
)
async def register_canonical_entity(
    payload: CanonicalEntityCreate,
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> CanonicalEntityResponse:
    """Create a dynamic canonical entity after validating client/portfolio scope."""
    return CanonicalEntityResponse.model_validate(create_canonical_entity(db, payload))


@router.post(
    "/source-artifacts",
    response_model=SourceArtifactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register source artifact",
    description="Registers immutable lineage metadata, schema/parser versions, and synthetic-data status for a source.",
)
async def register_source_artifact(
    payload: SourceArtifactCreate,
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> SourceArtifactResponse:
    """Create an idempotent, client-scoped source-artifact record."""
    return SourceArtifactResponse.model_validate(create_source_artifact(db, payload))


@router.post(
    "/processing-runs",
    response_model=ProcessingRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record processing run",
    description="Records which agent/service classified, parsed, validated, or normalized a source and with which contract version.",
)
async def record_processing_run(
    payload: ProcessingRunCreate,
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> ProcessingRunResponse:
    """Persist an auditable bounded processing run."""
    return ProcessingRunResponse.model_validate(create_processing_run(db, payload))


@router.post(
    "/rules",
    response_model=BusinessRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create business rule version",
    description="Creates a scoped and effective-dated tariff, market, solar-banking, constraint, or future configuration version.",
)
async def register_business_rule(
    payload: BusinessRuleCreate,
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> BusinessRuleResponse:
    """Persist a rule version while requiring explicit approval metadata for active rules."""
    return BusinessRuleResponse.model_validate(create_business_rule(db, payload))


@router.get(
    "/rules/effective",
    response_model=list[BusinessRuleResponse],
    summary="Resolve effective business rules",
    description="Returns approved rule versions effective at a requested time, enabling historical calculation replay.",
)
async def get_effective_business_rules(
    rule_key: str | None = None,
    scope_type: str | None = None,
    scope_key: str | None = None,
    effective_at: datetime | None = Query(None, description="ISO-8601 instant; defaults to current UTC time."),
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> list[BusinessRuleResponse]:
    """Resolve effective rules through optional key and scope filters."""
    resolved_at = effective_at or utc_now()
    return [BusinessRuleResponse.model_validate(row) for row in list_effective_rules(db, rule_key, scope_type, scope_key, resolved_at)]


@router.post(
    "/audit-events",
    response_model=AIExecutionAuditResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record AI execution audit",
    description="Records tenant scope, actor, capability, evidence references, tools, versions, confidence, and limitations.",
)
async def record_ai_execution(
    payload: AIExecutionAuditCreate,
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> AIExecutionAuditResponse:
    """Persist an AI execution envelope without exposing hidden chain-of-thought."""
    return AIExecutionAuditResponse.model_validate(create_audit_event(db, payload))


def decision_response(record) -> DecisionRecordResponse:
    """Convert a decision ORM record into the public contract and NLP narrative."""
    return DecisionRecordResponse(
        id=record.id,
        audit_event_id=record.audit_event_id,
        client_id=record.client_id,
        portfolio_id=record.portfolio_id,
        decision_type=record.decision_type,
        title=record.title,
        summary=record.summary,
        rationale=record.rationale,
        evidence=record.evidence,
        alternatives=record.alternatives,
        limitations=record.limitations,
        confidence=record.confidence,
        status=record.status,
        human_review_required=record.human_review_required,
        reviewed_by=record.reviewed_by,
        reviewed_at=record.reviewed_at,
        review_note=record.review_note,
        human_narrative=build_human_narrative(record),
        created_at=record.created_at,
    )


@router.post(
    "/decisions",
    response_model=DecisionRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record explainable decision",
    description="Stores a structured evidence-backed decision and generates a deterministic human-readable narrative.",
)
async def record_decision(
    payload: DecisionRecordCreate,
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> DecisionRecordResponse:
    """Persist a decision designed for both agent processing and specialist review."""
    return decision_response(create_decision(db, payload))


@router.get(
    "/decisions/{decision_id}",
    response_model=DecisionRecordResponse,
    summary="Get explainable decision",
    description="Returns a decision only within the explicitly supplied client scope, including evidence and human narrative.",
)
async def read_decision(
    decision_id: str,
    client_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> DecisionRecordResponse:
    """Retrieve an explainable decision through mandatory client scoping."""
    return decision_response(get_decision(db, decision_id, client_id))
