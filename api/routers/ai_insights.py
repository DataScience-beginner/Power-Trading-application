"""AI-1 routes for deterministic quality, explanation, and bounded assistance."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from api.schemas.ai_insights import (
    AssistantQueryRequest,
    AssistantQueryResponse,
    MarketExplanationRequest,
    MarketExplanationResponse,
    QualityAnalysisRequest,
    QualityRunResponse,
)
from api.security.ai_foundation import require_ai_foundation_access
from api.services.data_quality_service import get_quality_run, run_quality_analysis
from api.services.insight_assistant_service import answer_query
from api.services.market_explanation_service import explain_market
from database.config import get_db


router = APIRouter(prefix="/api/v1/ai-insights", tags=["ai-insights"])


@router.post(
    "/quality/analyze",
    response_model=QualityRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run deterministic data quality analysis",
    description="Evaluates scoped V0 files using a versioned dynamic policy and persists evidence-backed findings without correcting source data.",
)
async def analyze_data_quality(
    payload: QualityAnalysisRequest,
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> QualityRunResponse:
    """Run an auditable quality policy against client-scoped data."""
    return run_quality_analysis(db, payload)


@router.get(
    "/quality/runs/{run_id}",
    response_model=QualityRunResponse,
    summary="Get data quality run",
    description="Returns a persisted quality run and its findings only within mandatory client scope.",
)
async def read_quality_run(
    run_id: str,
    client_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> QualityRunResponse:
    """Read a complete quality result using tenant-safe scoping."""
    return get_quality_run(db, run_id, client_id)


@router.post(
    "/market/explain",
    response_model=MarketExplanationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Explain scoped market data",
    description="Creates a deterministic evidence-backed explanation and audit record from existing client-scoped facts.",
)
async def explain_market_data(
    payload: MarketExplanationRequest,
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> MarketExplanationResponse:
    """Explain recorded market facts without forecasting or executing an action."""
    return explain_market(db, payload)


@router.post(
    "/assistant/query",
    response_model=AssistantQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask bounded read-only energy assistant",
    description="Routes a question only to approved quality, coverage, cost, and schedule-data tools; arbitrary SQL and mutations are forbidden.",
)
async def query_energy_assistant(
    payload: AssistantQueryRequest,
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> AssistantQueryResponse:
    """Return a safe evidence-backed answer through deterministic intent routing."""
    return answer_query(db, payload)
