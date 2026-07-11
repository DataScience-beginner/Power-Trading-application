"""Tenant-scoped conversational orchestration over approved deterministic tools."""

from datetime import date, timedelta
import re
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.schemas.ai_insights import MarketExplanationRequest
from api.schemas.chatbot import ChatMessageResponse, ChatQueryRequest, ChatQueryResponse, ConversationCreateRequest, ConversationResponse
from api.security.chat_auth import authorize_scope
from api.services.chat_model_provider import GroqNarrativeProvider
from api.services.data_quality_service import latest_quality_summary
from api.services.insight_assistant_service import classify_intent
from api.services.market_explanation_service import explain_market
from api.services.forecasting_service import latest_solar_forecast
from database.chatbot_models import AppUser, ChatConversation, ChatMessage
from database.models import DailyFile, Portfolio


SUGGESTIONS = [
    "Are any expected files or blocks missing?",
    "Explain the recorded IEX cost for this period.",
    "Compare the recorded DOR and SCH quantities.",
    "How much data is available for this portfolio?",
    "Explain the latest solar generation forecast.",
]

SAFETY_PATTERNS = {
    "credential_request": [
        r"\b(password|credential|secret)\b",
        r"\bapi[ _-]?key\b",
        r"\bdatabase[ _-]?url\b",
        r"\bconnection string\b",
    ],
    "prompt_injection": [
        r"ignore (previous|all|the) instructions",
        r"\bsystem prompt\b",
        r"reveal (the |your )?prompt",
    ],
    "arbitrary_sql": [
        r"\b(select|insert|update|delete|drop|alter|truncate)\b.+\b(from|into|table|database)\b",
        r"\b(execute|run)\s+(raw\s+)?sql\b",
    ],
    "cross_tenant_request": [
        r"\b(another|other|different) client\b",
        r"\ball clients\b",
        r"\bcross[- ]client\b",
    ],
    "consequential_action": [
        r"\b(buy|purchase|sell)\b.+\b(mw|power|iex|market)\b",
        r"\b(place|submit|execute)\b.+\b(bid|trade|order)\b",
        r"\b(change|modify|update|delete|correct)\b.+\b(schedule|data|record|file)\b",
    ],
}

SAFETY_RESPONSES = {
    "credential_request": "I cannot reveal passwords, credentials, API keys, database URLs, or other secrets.",
    "prompt_injection": "I cannot reveal internal prompts or ignore the assistant's security instructions.",
    "arbitrary_sql": "I cannot execute user-supplied SQL or provide direct database access.",
    "cross_tenant_request": "I cannot access another client's data. This conversation is restricted to its authorized client and portfolio scope.",
    "consequential_action": "I cannot place bids or trades, buy or sell power, modify schedules, or change data. This assistant is read-only.",
}


def message_response(message: ChatMessage) -> ChatMessageResponse:
    return ChatMessageResponse.model_validate(message)


def conversation_response(conversation: ChatConversation) -> ConversationResponse:
    return ConversationResponse(
        id=conversation.id,
        client_id=conversation.client_id,
        portfolio_id=conversation.portfolio_id,
        title=conversation.title,
        status=conversation.status,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[message_response(item) for item in sorted(conversation.messages, key=lambda row: row.created_at)],
    )


def create_conversation(db: Session, user: AppUser, payload: ConversationCreateRequest) -> ChatConversation:
    """Create a conversation whose scope cannot later be changed by user text."""
    authorize_scope(db, user, payload.client_id, payload.portfolio_id)
    conversation = ChatConversation(
        user_id=user.id,
        client_id=payload.client_id,
        portfolio_id=payload.portfolio_id,
        title=payload.title,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation(db: Session, user: AppUser, conversation_id: str) -> ChatConversation:
    """Return only a conversation owned by the authenticated user."""
    conversation = db.query(ChatConversation).filter(
        ChatConversation.id == conversation_id,
        ChatConversation.user_id == user.id,
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    authorize_scope(db, user, conversation.client_id, conversation.portfolio_id)
    return conversation


def list_conversations(db: Session, user: AppUser) -> list[ChatConversation]:
    return db.query(ChatConversation).filter(ChatConversation.user_id == user.id).order_by(ChatConversation.updated_at.desc()).all()


def resolve_date_range(db: Session, conversation: ChatConversation, payload: ChatQueryRequest) -> tuple[date, date]:
    """Use explicit dates or latest available scoped V0 date, never an unbounded query."""
    if payload.start_date and payload.end_date:
        start, end = payload.start_date.date(), payload.end_date.date()
        if end < start or (end - start).days > 366:
            raise HTTPException(status_code=400, detail="Chat date range must be 0-366 days")
        return start, end
    query = db.query(func.max(DailyFile.trading_date)).join(Portfolio).filter(Portfolio.client_id == conversation.client_id)
    if conversation.portfolio_id:
        query = query.filter(Portfolio.id == conversation.portfolio_id)
    end = query.scalar() or date.today()
    return end - timedelta(days=29), end


def safety_violation(question: str) -> str | None:
    """Return the first governed safety category matched by natural user wording."""
    text = " ".join(question.lower().split())
    for category, patterns in SAFETY_PATTERNS.items():
        if any(re.search(pattern, text) for pattern in patterns):
            return category
    return None


def persist_message(db: Session, conversation_id: str, role: str, content: str, **metadata) -> ChatMessage:
    message = ChatMessage(conversation_id=conversation_id, role=role, content=content, **metadata)
    db.add(message)
    db.flush()
    return message


def answer_message(
    db: Session,
    user: AppUser,
    conversation_id: str,
    payload: ChatQueryRequest,
) -> ChatQueryResponse:
    """Answer through approved tools, then optionally narrate already-verified facts."""
    conversation = get_conversation(db, user, conversation_id)
    start_date, end_date = resolve_date_range(db, conversation, payload)
    user_message = persist_message(db, conversation.id, "user", payload.question, safety_status="submitted")
    violation = safety_violation(payload.question)
    intent = "unsupported" if violation else classify_intent(payload.question)

    if intent == "unsupported":
        content = SAFETY_RESPONSES.get(
            violation,
            "That question is outside the approved read-only tools. Ask about authorized data quality, coverage, recorded cost, or DOR/SCH information.",
        )
        assistant = persist_message(
            db,
            conversation.id,
            "assistant",
            content,
            intent="unsupported",
            provider="deterministic",
            model="safety-router-v1",
            prompt_version="chatbot-system-v1",
            limitations=[f"Request blocked by the read-only chatbot policy: {violation or 'unsupported_intent'}."],
            safety_status="blocked",
            confidence=100,
        )
    elif intent == "data_quality":
        summary = latest_quality_summary(db, conversation.client_id, conversation.portfolio_id)
        baseline = (
            "Latest quality finding counts: " + ", ".join(f"{key}={value}" for key, value in sorted(summary.items()))
            if summary
            else "No quality run exists for this scope. Run Data Quality Analysis first."
        )
        facts = {"intent": intent, "start_date": str(start_date), "end_date": str(end_date), **summary}
        result = GroqNarrativeProvider().narrate(payload.question, facts, baseline)
        limitations = [result.limitation] if result.limitation else []
        assistant = persist_message(
            db,
            conversation.id,
            "assistant",
            result.content,
            intent=intent,
            provider=result.provider,
            model=result.model,
            prompt_version="chatbot-system-v1",
            tool_calls=[{"tool": "latest_quality_summary", "safety": "read_only"}],
            evidence=[{"metric": key, "value": value} for key, value in summary.items()],
            limitations=limitations,
            safety_status="allowed",
            confidence=100 if summary else 40,
            token_usage=result.token_usage,
        )
    elif intent == "solar_forecast":
        if not conversation.portfolio_id:
            content = "Select a portfolio-scoped conversation before asking for a solar generation forecast."
            assistant = persist_message(
                db, conversation.id, "assistant", content, intent=intent, provider="deterministic",
                model="forecast-explainer-v1", prompt_version="chatbot-system-v1",
                limitations=["Solar forecasts require one authorized portfolio."], safety_status="blocked", confidence=100,
            )
        else:
            try:
                forecast = latest_solar_forecast(db, conversation.client_id, conversation.portfolio_id)
                total_p50 = round(sum(point.p50_kwh for point in forecast.points), 2)
                facts = {
                    "intent": intent,
                    "forecast_run_id": forecast.run_id,
                    "horizon_days": len(forecast.points),
                    "total_p50_kwh": total_p50,
                    "confidence_pct": round(forecast.confidence * 100),
                    "mape_pct": forecast.backtest_metrics.get("mape_pct"),
                    "weather_source": forecast.weather_source,
                    "data_classification": forecast.data_classification,
                }
                baseline = (
                    f"The latest {len(forecast.points)}-day solar forecast has P50 generation of {total_p50:,.0f} kWh "
                    f"with {forecast.confidence:.0%} confidence. Weather source is {forecast.weather_source}; "
                    f"generation history is classified as {forecast.data_classification}."
                )
                result = GroqNarrativeProvider().narrate(payload.question, facts, baseline)
                limitations = list(forecast.limitations)
                if result.limitation:
                    limitations.append(result.limitation)
                assistant = persist_message(
                    db, conversation.id, "assistant", result.content, intent=intent, provider=result.provider,
                    model=result.model, prompt_version="chatbot-system-v1",
                    tool_calls=[{"tool": "latest_solar_forecast", "safety": "read_only"}],
                    evidence=[{"forecast_run_id": forecast.run_id, "contract_version": forecast.contract_version}],
                    limitations=limitations, safety_status="allowed", confidence=round(forecast.confidence * 100),
                    token_usage=result.token_usage,
                )
            except HTTPException as exc:
                assistant = persist_message(
                    db, conversation.id, "assistant",
                    "No solar forecast exists for this portfolio yet. Open AI Predict and run the governed solar forecast first.",
                    intent=intent, provider="deterministic", model="forecast-explainer-v1",
                    prompt_version="chatbot-system-v1", limitations=[str(exc.detail)], safety_status="allowed", confidence=100,
                )
    else:
        explanation = explain_market(
            db,
            MarketExplanationRequest(
                client_id=conversation.client_id,
                portfolio_id=conversation.portfolio_id,
                start_date=start_date,
                end_date=end_date,
                question=payload.question,
                correlation_id=f"chat-{uuid4()}",
            ),
        )
        facts = {item.name: item.value for item in explanation.metrics}
        facts.update({"intent": intent, "start_date": str(start_date), "end_date": str(end_date)})
        result = GroqNarrativeProvider().narrate(payload.question, facts, explanation.answer)
        limitations = list(explanation.limitations)
        if result.limitation:
            limitations.append(result.limitation)
        assistant = persist_message(
            db,
            conversation.id,
            "assistant",
            result.content,
            intent=intent,
            provider=result.provider,
            model=result.model,
            prompt_version="chatbot-system-v1",
            tool_calls=[{"tool": "scoped_market_explanation", "safety": "read_only"}],
            evidence=[item.model_dump(mode="json") for item in explanation.evidence],
            limitations=limitations,
            safety_status="allowed",
            confidence=round(explanation.confidence * 100),
            token_usage=result.token_usage,
        )

    conversation.updated_at = assistant.created_at
    db.commit()
    db.refresh(user_message)
    db.refresh(assistant)
    return ChatQueryResponse(
        conversation_id=conversation.id,
        user_message=message_response(user_message),
        assistant_message=message_response(assistant),
        suggested_questions=SUGGESTIONS,
    )
