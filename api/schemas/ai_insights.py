"""Typed AI-1 contracts for quality, explanations, and bounded assistance."""

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from api.schemas.ai_foundation import EvidenceItem, ScopeContract


Severity = Literal["critical", "high", "medium", "low", "info"]


class QualityPolicy(BaseModel):
    """Versioned, client-overridable quality expectations—not final domain truth."""

    policy_version: str = Field("data-quality-v1", max_length=40)
    expected_report_types: list[str] = Field(
        default_factory=lambda: ["DOR-GDAM", "DOR-DAM", "DOR-RTM", "SCH-GDAM", "SCH-DAM", "SCH-RTM"],
        description="Expected source classifications for this run; override as markets evolve.",
    )
    expected_blocks_per_file: int = Field(96, ge=1, le=10000)
    minimum_rate: float = Field(0, description="Rates below this threshold are flagged.")
    maximum_rate: float | None = Field(None, gt=0, description="Optional approved upper threshold.")
    allow_negative_quantity: bool = False
    require_time_block_start: bool = True


class QualityAnalysisRequest(ScopeContract):
    """Request a deterministic quality run over a bounded date range."""

    start_date: date
    end_date: date
    correlation_id: str = Field(..., min_length=4, max_length=100)
    data_classification: Literal["synthetic", "actual", "mixed", "unknown"] = "unknown"
    policy: QualityPolicy = Field(default_factory=QualityPolicy)

    @model_validator(mode="after")
    def validate_range(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        if (self.end_date - self.start_date).days > 366:
            raise ValueError("quality analysis range cannot exceed 366 days")
        return self


class QualityFindingResponse(BaseModel):
    """Finding understandable by both agents and specialists."""

    id: str
    run_id: str
    client_id: int
    portfolio_id: int | None
    daily_file_id: int | None
    rule_id: str
    rule_version: str
    severity: Severity
    category: str
    title: str
    description: str
    evidence: list[dict[str, Any]]
    recommended_action: str
    confidence: float
    status: str
    detected_at: datetime

    model_config = {"from_attributes": True}


class QualityRunResponse(BaseModel):
    """Complete deterministic quality result with reproducibility metadata."""

    id: str
    correlation_id: str
    client_id: int
    portfolio_id: int | None
    start_date: date
    end_date: date
    policy_version: str
    policy_configuration: dict[str, Any]
    engine_version: str
    status: str
    files_evaluated: int
    transactions_evaluated: int
    finding_counts: dict[str, int]
    data_classification: str
    started_at: datetime
    completed_at: datetime | None
    findings: list[QualityFindingResponse]
    limitations: list[str]


class MarketExplanationRequest(ScopeContract):
    """Request an evidence-backed explanation from existing trading facts."""

    start_date: date
    end_date: date
    question: str = Field(..., min_length=3, max_length=500)
    correlation_id: str = Field(..., min_length=4, max_length=100)

    @model_validator(mode="after")
    def validate_range(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        if (self.end_date - self.start_date).days > 366:
            raise ValueError("explanation range cannot exceed 366 days")
        return self


class ExplanationMetric(BaseModel):
    """Named metric used by deterministic explanation logic."""

    name: str
    value: float | int | str
    unit: str | None = None


class MarketExplanationResponse(BaseModel):
    """Evidence-backed explanation; never an authoritative schedule or forecast."""

    explanation_id: str
    client_id: int
    portfolio_id: int | None
    question: str
    answer: str
    summary: str
    metrics: list[ExplanationMetric]
    evidence: list[EvidenceItem]
    confidence: float = Field(..., ge=0, le=1)
    limitations: list[str]
    data_classification: str
    engine: Literal["deterministic-v1"] = "deterministic-v1"
    human_review_required: bool


class AssistantQueryRequest(MarketExplanationRequest):
    """Ask a bounded read-only question through the approved insight tools."""

    conversation_id: str | None = Field(None, max_length=100)


class AssistantQueryResponse(BaseModel):
    """Read-only assistant response with disclosed routing and evidence."""

    conversation_id: str
    intent: Literal["data_quality", "market_cost", "schedule_variance", "data_coverage", "unsupported"]
    answer: str
    suggested_questions: list[str]
    explanation: MarketExplanationResponse | None = None
    quality_summary: dict[str, int] | None = None
    safety_notice: str
