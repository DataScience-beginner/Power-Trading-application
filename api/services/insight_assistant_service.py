"""Bounded intent router for the AI-1 read-only assistant."""

from uuid import uuid4

from sqlalchemy.orm import Session

from api.schemas.ai_insights import AssistantQueryRequest, AssistantQueryResponse
from api.services.data_quality_service import latest_quality_summary
from api.services.market_explanation_service import explain_market


def classify_intent(question: str) -> str:
    """Classify only supported read-only intents using deterministic keywords."""
    text = question.lower()
    if "solar" in text and any(word in text for word in ["forecast", "generation", "p10", "p50", "p90"]):
        return "solar_forecast"
    prohibited_requests = [
        "forecast",
        "predict",
        "place a trade",
        "place trade",
        "submit a bid",
        "execute a trade",
        "trade automatically",
        "buy automatically",
        "sell automatically",
        "change the schedule",
        "correct the data",
        "delete the data",
    ]
    if any(phrase in text for phrase in prohibited_requests):
        return "unsupported"
    if any(word in text for word in ["quality", "missing", "duplicate", "invalid", "complete"]):
        return "data_quality"
    if any(word in text for word in ["schedule", "dor", "sch", "variance", "deviation"]):
        return "schedule_variance"
    if any(word in text for word in ["cost", "price", "rate", "iex", "tneb", "market"]):
        return "market_cost"
    if any(word in text for word in ["file", "data", "coverage", "transaction"]):
        return "data_coverage"
    return "unsupported"


def answer_query(db: Session, request: AssistantQueryRequest) -> AssistantQueryResponse:
    """Route a question to approved deterministic tools without arbitrary SQL or actions."""
    intent = classify_intent(request.question)
    conversation_id = request.conversation_id or str(uuid4())
    suggestions = [
        "Are any expected reports missing?",
        "Explain the recorded cost for this period.",
        "How many files and interval records are available?",
        "Do the DOR and SCH records need review?",
    ]
    safety = "Read-only explanation. No forecast, schedule change, data correction, bid, or trade was executed."

    if intent == "data_quality":
        summary = latest_quality_summary(db, request.client_id, request.portfolio_id)
        if summary:
            answer = "Latest quality findings by severity: " + ", ".join(f"{key}={value}" for key, value in sorted(summary.items())) + "."
        else:
            answer = "No persisted quality run exists for this scope. Run Data Quality Analysis first."
        return AssistantQueryResponse(
            conversation_id=conversation_id,
            intent="data_quality",
            answer=answer,
            suggested_questions=suggestions,
            quality_summary=summary,
            safety_notice=safety,
        )

    if intent in {"market_cost", "schedule_variance", "data_coverage"}:
        explanation = explain_market(db, request)
        prefix = {
            "market_cost": "Cost view: ",
            "schedule_variance": "Schedule-data view: ",
            "data_coverage": "Coverage view: ",
        }[intent]
        return AssistantQueryResponse(
            conversation_id=conversation_id,
            intent=intent,
            answer=prefix + explanation.answer,
            suggested_questions=suggestions,
            explanation=explanation,
            safety_notice=safety,
        )

    return AssistantQueryResponse(
        conversation_id=conversation_id,
        intent="unsupported",
        answer="That question is outside the approved AI-1 tools. Ask about data quality, coverage, recorded cost, or DOR/SCH schedule data.",
        suggested_questions=suggestions,
        safety_notice=safety,
    )
