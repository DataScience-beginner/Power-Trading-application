"""Isolated deterministic tests for AI-1 quality and market insight services."""

from datetime import date, datetime

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.schemas.ai_insights import AssistantQueryRequest, MarketExplanationRequest, QualityAnalysisRequest, QualityPolicy
from api.services.data_quality_service import get_quality_run, run_quality_analysis
from api.services.insight_assistant_service import answer_query, classify_intent
from api.services.market_explanation_service import explain_market
from api.services.narrative_provider import DeterministicNarrativeProvider, MarketNarrativeFacts
from database.ai_foundation_models import AIExecutionAudit, DecisionRecord
from database.ai_insights_models import DataQualityFinding, DataQualityRun
from database.config import Base
from database.models import Client, DailyFile, Portfolio, Transaction


@pytest.fixture()
def db():
    """Provide a complete in-memory schema that never touches Railway."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    client = Client(entity_id="AI1-CLIENT", entity_name="AI-1 Test Client")
    session.add(client)
    session.flush()
    portfolio = Portfolio(client_id=client.id, portfolio_code="AI1-PORT", portfolio_name="AI-1 Portfolio")
    session.add(portfolio)
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def scope(db) -> tuple[int, int]:
    client = db.query(Client).filter(Client.entity_id == "AI1-CLIENT").one()
    portfolio = db.query(Portfolio).filter(Portfolio.client_id == client.id).one()
    return client.id, portfolio.id


def seed_file(db, portfolio_id: int, report_type: str = "DOR-DAM", duplicate_slot: bool = False) -> DailyFile:
    """Create a tiny configurable V0 file fixture for policy tests."""
    file = DailyFile(
        portfolio_id=portfolio_id,
        trading_date=date(2026, 1, 1),
        delivery_date=date(2026, 1, 1),
        main_category="DOR",
        sub_category="DAM",
        report_type=report_type,
        original_filename=f"{report_type}.xlsx",
    )
    db.add(file)
    db.flush()
    slots = ["00:00 - 00:15", "00:00 - 00:15" if duplicate_slot else "00:15 - 00:30"]
    for index, slot in enumerate(slots):
        db.add(
            Transaction(
                daily_file_id=file.id,
                date=date(2026, 1, 1),
                time_slot=slot,
                time_block_start=datetime(2026, 1, 1, 0, index * 15),
                transaction_type="buy",
                quantity_mw=10 + index,
                rate_per_mwh=3000 + index * 100,
                amount=(10 + index) * (3000 + index * 100),
            )
        )
    db.commit()
    return file


def quality_request(client_id: int, portfolio_id: int, expected_blocks: int = 2) -> QualityAnalysisRequest:
    return QualityAnalysisRequest(
        client_id=client_id,
        portfolio_id=portfolio_id,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 1),
        correlation_id="quality-test-001",
        data_classification="synthetic",
        policy=QualityPolicy(expected_report_types=["DOR-DAM"], expected_blocks_per_file=expected_blocks),
    )


def test_clean_dynamic_policy_run_persists_no_findings(db) -> None:
    client_id, portfolio_id = scope(db)
    seed_file(db, portfolio_id)
    result = run_quality_analysis(db, quality_request(client_id, portfolio_id))
    assert result.files_evaluated == 1
    assert result.transactions_evaluated == 2
    assert result.findings == []
    assert result.data_classification == "synthetic"
    assert get_quality_run(db, result.id, client_id).id == result.id


def test_missing_and_duplicate_data_produce_evidence_backed_findings(db) -> None:
    client_id, portfolio_id = scope(db)
    seed_file(db, portfolio_id, duplicate_slot=True)
    request = quality_request(client_id, portfolio_id, expected_blocks=96)
    request.policy.expected_report_types = ["DOR-DAM", "SCH-DAM"]
    result = run_quality_analysis(db, request)
    rule_ids = {item.rule_id for item in result.findings}
    assert "coverage.missing_report_types" in rule_ids
    assert "interval.block_count" in rule_ids
    assert "interval.duplicate_blocks" in rule_ids
    assert all(item.evidence and item.recommended_action for item in result.findings)
    assert db.query(DataQualityFinding).filter(DataQualityFinding.run_id == result.id).count() == 3


def test_no_files_is_explicit_not_a_confident_success(db) -> None:
    client_id, portfolio_id = scope(db)
    result = run_quality_analysis(db, quality_request(client_id, portfolio_id))
    assert result.finding_counts["high"] == 1
    assert result.findings[0].rule_id == "coverage.no_files"


def test_market_explanation_records_audit_decision_and_limitations(db) -> None:
    client_id, portfolio_id = scope(db)
    seed_file(db, portfolio_id)
    result = explain_market(
        db,
        MarketExplanationRequest(
            client_id=client_id,
            portfolio_id=portfolio_id,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 1),
            question="Explain the recorded market cost",
            correlation_id="explain-test-001",
        ),
    )
    assert result.engine == "deterministic-v1"
    assert result.evidence
    assert result.limitations
    assert result.data_classification == "unknown-v0-lineage"
    assert db.query(AIExecutionAudit).filter(AIExecutionAudit.id == result.explanation_id).count() == 1
    assert db.query(DecisionRecord).filter(DecisionRecord.audit_event_id == result.explanation_id).count() == 1


def test_bounded_assistant_routes_or_refuses_without_actions(db) -> None:
    client_id, portfolio_id = scope(db)
    assert classify_intent("Are files missing?") == "data_quality"
    assert classify_intent("Predict the weather in 2035") == "unsupported"
    assert classify_intent("Forecast tomorrow and place an IEX trade automatically") == "unsupported"
    assert classify_intent("Explain the recorded IEX cost") == "market_cost"
    response = answer_query(
        db,
        AssistantQueryRequest(
            client_id=client_id,
            portfolio_id=portfolio_id,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 1),
            question="Predict the weather in 2035",
            correlation_id="assistant-test-001",
        ),
    )
    assert response.intent == "unsupported"
    assert "No forecast" in response.safety_notice


def test_cross_client_portfolio_scope_is_rejected(db) -> None:
    _, portfolio_id = scope(db)
    other = Client(entity_id="AI1-OTHER", entity_name="Other AI-1 Client")
    db.add(other)
    db.commit()
    with pytest.raises(HTTPException) as error:
        run_quality_analysis(db, quality_request(other.id, portfolio_id))
    assert error.value.status_code == 404


def test_ai_insights_migration_is_additive() -> None:
    migration = open("database/migrations/ai_insights_v1.sql", encoding="utf-8").read()
    assert "CREATE TABLE IF NOT EXISTS data_quality_runs" in migration
    assert "CREATE TABLE IF NOT EXISTS data_quality_findings" in migration
    assert "DROP TABLE" not in migration.upper()


def test_narrative_provider_cannot_change_structured_facts() -> None:
    facts = MarketNarrativeFacts(
        file_count=2,
        transaction_count=192,
        total_cost=125000,
        total_quantity=20,
        average_rate=6250,
    )
    text = DeterministicNarrativeProvider().market_summary(facts)
    assert "2 files" in text
    assert "192 interval records" in text
    assert "₹125,000.00" in text
    assert "MW-blocks" in text
