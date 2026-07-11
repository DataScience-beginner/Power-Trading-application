"""Pydantic contracts for the AI-0 trust and governance foundation."""

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


ContractVersion = Literal["ai-foundation-v1"]
RecordStatus = Literal["draft", "active", "inactive", "deprecated"]


def utc_now() -> datetime:
    """Return naive UTC to match the application's existing timestamp convention."""
    return datetime.now(UTC).replace(tzinfo=None)


class ScopeContract(BaseModel):
    """Tenant-safe scope carried by every persisted AI-0 operation."""

    client_id: int = Field(..., gt=0, description="Required client/tenant identifier.")
    portfolio_id: int | None = Field(None, gt=0, description="Optional portfolio within the client.")


class CanonicalEntityCreate(ScopeContract):
    """Create a versioned flexible entity without changing the database schema."""

    entity_type: str = Field(..., min_length=2, max_length=80, description="Configurable type such as site, meter, solar_asset, or contract.")
    external_key: str = Field(..., min_length=1, max_length=180, description="Stable source/business identifier.")
    display_name: str = Field(..., min_length=1, max_length=255)
    parent_entity_id: str | None = None
    schema_version: str = Field("canonical-v1", max_length=40)
    version: int = Field(1, ge=1)
    attributes: dict[str, Any] = Field(default_factory=dict, description="Versioned type-specific attributes.")
    valid_from: datetime = Field(default_factory=utc_now)
    valid_to: datetime | None = None
    status: RecordStatus = "active"

    @model_validator(mode="after")
    def validate_dates(self):
        if self.valid_to and self.valid_to <= self.valid_from:
            raise ValueError("valid_to must be after valid_from")
        return self


class CanonicalEntityResponse(CanonicalEntityCreate):
    """Persisted canonical entity returned to agents and humans."""

    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SourceArtifactCreate(ScopeContract):
    """Register immutable lineage metadata for a source artifact."""

    source_type: str = Field(..., min_length=2, max_length=80, description="File, email, API payload, meter feed, or another configured source.")
    original_name: str = Field(..., min_length=1, max_length=500)
    content_checksum: str = Field(..., min_length=16, max_length=128, description="Content hash used for idempotency.")
    storage_uri: str | None = Field(None, max_length=1000, description="Reference only; credentials are forbidden.")
    source_schema_version: str = Field("unknown", max_length=80)
    parser_name: str | None = Field(None, max_length=120)
    parser_version: str | None = Field(None, max_length=40)
    artifact_version: int = Field(1, ge=1)
    canonical_entity_id: str | None = None
    supersedes_artifact_id: str | None = None
    status: str = Field("registered", max_length=30)
    is_synthetic: bool = Field(False, description="Explicitly distinguishes mock/test data from actual client data.")
    artifact_metadata: dict[str, Any] = Field(default_factory=dict)
    observed_at: datetime | None = None


class SourceArtifactResponse(SourceArtifactCreate):
    """Registered source artifact with lineage identifier."""

    id: str
    registered_at: datetime

    model_config = {"from_attributes": True}


class ProcessingRunCreate(ScopeContract):
    """Record a bounded agent or service execution against a source artifact."""

    correlation_id: str = Field(..., min_length=4, max_length=100)
    source_artifact_id: str
    run_type: str = Field(..., min_length=2, max_length=80)
    executor_type: Literal["agent", "human", "service"] = "agent"
    executor_id: str = Field(..., min_length=1, max_length=120)
    executor_version: str = Field(..., min_length=1, max_length=40)
    contract_version: ContractVersion = "ai-foundation-v1"
    status: Literal["started", "completed", "failed", "cancelled"] = "started"
    input_summary: dict[str, Any] = Field(default_factory=dict)
    output_summary: dict[str, Any] = Field(default_factory=dict)
    error_details: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None


class ProcessingRunResponse(ProcessingRunCreate):
    """Persisted processing run with immutable execution identity."""

    id: str

    model_config = {"from_attributes": True}


class BusinessRuleCreate(BaseModel):
    """Create an effective-dated, scoped, versioned business rule."""

    rule_key: str = Field(..., min_length=2, max_length=160)
    rule_type: str = Field(..., min_length=2, max_length=80)
    scope_type: Literal["global", "jurisdiction", "client", "portfolio", "asset"] = "global"
    scope_key: str = Field("global", min_length=1, max_length=160)
    jurisdiction: str | None = Field(None, max_length=80)
    version: int = Field(..., ge=1)
    schema_version: str = Field("rule-v1", max_length=40)
    configuration: dict[str, Any] = Field(..., description="Rule payload validated by the rule's schema version.")
    valid_from: datetime
    valid_to: datetime | None = None
    status: Literal["draft", "approved", "active", "retired"] = "draft"
    approved_by: str | None = Field(None, max_length=120)
    approval_note: str | None = None

    @model_validator(mode="after")
    def validate_dates_and_approval(self):
        if self.valid_to and self.valid_to <= self.valid_from:
            raise ValueError("valid_to must be after valid_from")
        if self.status in {"approved", "active"} and not self.approved_by:
            raise ValueError("approved_by is required for approved or active rules")
        return self


class BusinessRuleResponse(BusinessRuleCreate):
    """Persisted business-rule version."""

    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AIExecutionAuditCreate(ScopeContract):
    """Record the complete evidence envelope for an AI or agent execution."""

    correlation_id: str = Field(..., min_length=4, max_length=100)
    actor_type: Literal["agent", "human", "service"]
    actor_id: str = Field(..., min_length=1, max_length=120)
    agent_id: str | None = Field(None, max_length=120)
    agent_version: str | None = Field(None, max_length=40)
    capability: str = Field(..., min_length=2, max_length=120)
    contract_version: ContractVersion = "ai-foundation-v1"
    model_provider: str | None = Field(None, max_length=80)
    model_name: str | None = Field(None, max_length=120)
    model_version: str | None = Field(None, max_length=80)
    prompt_version: str | None = Field(None, max_length=80)
    input_references: list[dict[str, Any]] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    output_payload: dict[str, Any] = Field(default_factory=dict)
    confidence: float | None = Field(None, ge=0, le=1)
    status: Literal["completed", "failed", "blocked", "requires_review"] = "completed"
    limitations: list[str] = Field(default_factory=list)


class AIExecutionAuditResponse(AIExecutionAuditCreate):
    """Persisted execution audit returned without hidden chain-of-thought."""

    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EvidenceItem(BaseModel):
    """Traceable evidence supporting a decision."""

    source_type: str = Field(..., min_length=2, max_length=80)
    source_id: str = Field(..., min_length=1, max_length=180)
    metric: str = Field(..., min_length=1, max_length=160)
    value: Any
    unit: str | None = Field(None, max_length=40)
    observed_at: datetime | None = None


class DecisionRecordCreate(ScopeContract):
    """Create a structured decision that both humans and agents can interpret."""

    audit_event_id: str | None = None
    decision_type: str = Field(..., min_length=2, max_length=100)
    title: str = Field(..., min_length=3, max_length=255)
    summary: str = Field(..., min_length=3)
    rationale: list[str] = Field(..., min_length=1)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    confidence: float | None = Field(None, ge=0, le=1)
    status: Literal["proposed", "accepted", "rejected", "superseded"] = "proposed"
    human_review_required: bool = True


class DecisionRecordResponse(DecisionRecordCreate):
    """Persisted structured decision plus deterministic human narrative."""

    id: str
    human_narrative: str
    created_at: datetime
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    review_note: str | None = None


class CapabilityDefinition(BaseModel):
    """Agent-readable description of an approved AI-0 capability."""

    capability_id: str
    purpose: str
    endpoint: str
    method: str
    safety: str
    writes_data: bool
    human_review: str
    contract_version: ContractVersion = "ai-foundation-v1"


class CapabilityCatalogResponse(BaseModel):
    """Discoverable AI-0 capability and governance catalog."""

    foundation_version: str
    canonical_schema_status: str
    mock_data_status: str
    principles: list[str]
    capabilities: list[CapabilityDefinition]
