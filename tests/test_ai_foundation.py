"""Deterministic, isolated tests for the additive AI Phase 0 foundation."""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.schemas.ai_foundation import (
    AIExecutionAuditCreate,
    BusinessRuleCreate,
    CanonicalEntityCreate,
    DecisionRecordCreate,
    EvidenceItem,
    ProcessingRunCreate,
    SourceArtifactCreate,
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
from database.ai_foundation_models import BusinessRuleVersion
from database.config import Base
from database.models import Client, Portfolio
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def db():
    """Provide an in-memory database that never reads or writes Railway."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    client = Client(entity_id="TEST-CLIENT", entity_name="Test Client")
    session.add(client)
    session.flush()
    portfolio = Portfolio(client_id=client.id, portfolio_code="TEST-PORTFOLIO", portfolio_name="Test Portfolio")
    session.add(portfolio)
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def scope_ids(db) -> tuple[int, int]:
    client = db.query(Client).filter(Client.entity_id == "TEST-CLIENT").one()
    portfolio = db.query(Portfolio).filter(Portfolio.client_id == client.id).one()
    return client.id, portfolio.id


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def test_dynamic_entity_and_lineage_workflow(db) -> None:
    client_id, portfolio_id = scope_ids(db)
    entity = create_canonical_entity(
        db,
        CanonicalEntityCreate(
            client_id=client_id,
            portfolio_id=portfolio_id,
            entity_type="solar_asset",
            external_key="SOLAR-001",
            display_name="Future Solar Configuration",
            attributes={"capacity": 5, "capacity_unit": "MW", "technology": "future-configurable"},
        ),
    )
    assert entity.attributes["capacity_unit"] == "MW"

    artifact = create_source_artifact(
        db,
        SourceArtifactCreate(
            client_id=client_id,
            portfolio_id=portfolio_id,
            canonical_entity_id=entity.id,
            source_type="market_file",
            original_name="synthetic-dam.xlsx",
            content_checksum="a" * 64,
            source_schema_version="synthetic-v0",
            parser_name="test-parser",
            parser_version="0.1",
            is_synthetic=True,
        ),
    )
    assert artifact.is_synthetic is True

    run = create_processing_run(
        db,
        ProcessingRunCreate(
            client_id=client_id,
            portfolio_id=portfolio_id,
            correlation_id="test-run-001",
            source_artifact_id=artifact.id,
            run_type="validation",
            executor_id="data-quality-agent",
            executor_version="1.0.0",
            status="completed",
            output_summary={"findings": 0},
        ),
    )
    assert run.contract_version == "ai-foundation-v1"


def test_effective_dated_rules_support_change_without_schema_change(db) -> None:
    now = utc_now()
    create_business_rule(
        db,
        BusinessRuleCreate(
            rule_key="solar.bank.validity",
            rule_type="solar_banking",
            scope_type="jurisdiction",
            scope_key="TN",
            jurisdiction="Tamil Nadu",
            version=1,
            configuration={"validity": 1, "unit": "month", "expiry_policy": "end_of_period"},
            valid_from=now - timedelta(days=10),
            status="active",
            approved_by="domain-specialist",
        ),
    )
    rules = list_effective_rules(db, "solar.bank.validity", "jurisdiction", "TN", now)
    assert len(rules) == 1
    assert isinstance(rules[0], BusinessRuleVersion)
    assert rules[0].configuration["unit"] == "month"


def test_audit_and_human_readable_decision(db) -> None:
    client_id, portfolio_id = scope_ids(db)
    audit = create_audit_event(
        db,
        AIExecutionAuditCreate(
            client_id=client_id,
            portfolio_id=portfolio_id,
            correlation_id="decision-001",
            actor_type="agent",
            actor_id="market-explanation-agent",
            agent_id="market-explanation",
            agent_version="0.1.0",
            capability="market.explain",
            input_references=[{"source_type": "analytics", "source_id": "snapshot-001"}],
            confidence=0.82,
            limitations=["Synthetic V0 evidence"],
        ),
    )
    decision = create_decision(
        db,
        DecisionRecordCreate(
            audit_event_id=audit.id,
            client_id=client_id,
            portfolio_id=portfolio_id,
            decision_type="data_quality_explanation",
            title="Review synthetic market snapshot",
            summary="The current result is suitable for workflow testing only.",
            rationale=["The source artifact is explicitly marked synthetic."],
            evidence=[EvidenceItem(source_type="audit", source_id=audit.id, metric="confidence", value=0.82)],
            limitations=["Not production client evidence"],
            confidence=0.82,
        ),
    )
    narrative = build_human_narrative(decision)
    assert "Confidence: 82%" in narrative
    assert "Human review is required" in narrative
    assert get_decision(db, decision.id, client_id).id == decision.id


def test_cross_client_scope_is_rejected(db) -> None:
    client_id, portfolio_id = scope_ids(db)
    other_client = Client(entity_id="OTHER", entity_name="Other Client")
    db.add(other_client)
    db.commit()

    with pytest.raises(HTTPException) as error:
        create_canonical_entity(
            db,
            CanonicalEntityCreate(
                client_id=other_client.id,
                portfolio_id=portfolio_id,
                entity_type="meter",
                external_key="METER-X",
                display_name="Invalid Cross-Scope Meter",
            ),
        )
    assert error.value.status_code == 404


def test_active_rule_requires_human_approval() -> None:
    with pytest.raises(ValueError):
        BusinessRuleCreate(
            rule_key="iex.product.validity",
            rule_type="market_rule",
            version=1,
            configuration={"validity": 1, "unit": "day"},
            valid_from=utc_now(),
            status="active",
        )


def test_service_authentication_fails_closed(monkeypatch) -> None:
    monkeypatch.delenv("AI_FOUNDATION_API_KEY", raising=False)
    with pytest.raises(HTTPException) as disabled:
        require_ai_foundation_access("anything")
    assert disabled.value.status_code == 503

    monkeypatch.setenv("AI_FOUNDATION_API_KEY", "test-secret")
    with pytest.raises(HTTPException) as unauthorized:
        require_ai_foundation_access("wrong-secret")
    assert unauthorized.value.status_code == 401
    assert require_ai_foundation_access("test-secret") == "service-authenticated"


def test_additive_migration_tracks_all_foundation_tables() -> None:
    migration = (ROOT / "database/migrations/ai_foundation_v1.sql").read_text(encoding="utf-8")
    for table_name in [
        "canonical_entities",
        "source_artifacts",
        "processing_runs",
        "business_rule_versions",
        "ai_execution_audits",
        "decision_records",
    ]:
        assert f"CREATE TABLE IF NOT EXISTS {table_name}" in migration
