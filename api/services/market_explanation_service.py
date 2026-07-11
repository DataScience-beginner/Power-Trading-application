"""Deterministic market explanations built from scoped structured evidence."""

from collections import Counter

from sqlalchemy.orm import Session

from api.schemas.ai_foundation import AIExecutionAuditCreate, DecisionRecordCreate, EvidenceItem
from api.schemas.ai_insights import ExplanationMetric, MarketExplanationRequest, MarketExplanationResponse
from api.services.ai_foundation_service import create_audit_event, create_decision, validate_scope
from api.services.narrative_provider import MarketNarrativeFacts, get_narrative_provider
from database.models import DailyFile, Portfolio, Transaction


def scoped_queries(db: Session, request: MarketExplanationRequest):
    """Build client/date/portfolio-scoped file and transaction queries."""
    file_query = db.query(DailyFile).join(Portfolio).filter(
        Portfolio.client_id == request.client_id,
        DailyFile.trading_date >= request.start_date,
        DailyFile.trading_date <= request.end_date,
    )
    txn_query = db.query(Transaction).join(DailyFile).join(Portfolio).filter(
        Portfolio.client_id == request.client_id,
        Transaction.date >= request.start_date,
        Transaction.date <= request.end_date,
    )
    if request.portfolio_id:
        file_query = file_query.filter(Portfolio.id == request.portfolio_id)
        txn_query = txn_query.filter(Portfolio.id == request.portfolio_id)
    return file_query, txn_query


def explain_market(db: Session, request: MarketExplanationRequest) -> MarketExplanationResponse:
    """Explain V0 market facts with explicit evidence, confidence, and limitations."""
    validate_scope(db, request.client_id, request.portfolio_id)
    file_query, txn_query = scoped_queries(db, request)
    files = file_query.all()
    transactions = txn_query.all()
    total_transactions = len(transactions)
    buy_transactions = [txn for txn in transactions if txn.transaction_type == "buy"]
    total_cost = float(sum(txn.amount or 0 for txn in buy_transactions))
    total_quantity = float(sum(txn.quantity_mw or 0 for txn in buy_transactions))
    avg_rate = float(sum(txn.rate_per_mwh or 0 for txn in buy_transactions) / len(buy_transactions)) if buy_transactions else 0
    buy_count = len(buy_transactions)
    scheduling_count = txn_query.filter(Transaction.transaction_type == "scheduling").count()
    report_counts = Counter(file.report_type for file in files)
    report_by_file_id = {file.id: file.report_type for file in files}
    dor_quantity = sum(
        txn.quantity_mw or 0
        for txn in transactions
        if report_by_file_id.get(txn.daily_file_id, "").startswith("DOR")
    )
    sch_quantity = sum(
        txn.quantity_mw or txn.total_quantity_mw or txn.net_scheduled_mw or 0
        for txn in transactions
        if report_by_file_id.get(txn.daily_file_id, "").startswith("SCH")
    )
    schedule_variance = dor_quantity - sch_quantity

    provider = get_narrative_provider()
    summary = provider.market_summary(
        MarketNarrativeFacts(
            file_count=len(files),
            transaction_count=total_transactions,
            total_cost=total_cost,
            total_quantity=total_quantity,
            average_rate=avg_rate,
        )
    )
    if not files:
        confidence = 0.0
        review = True
    else:
        confidence = 0.85 if total_transactions else 0.45
        review = total_transactions == 0

    evidence = [
        EvidenceItem(source_type="v0_aggregate", source_id="daily_files", metric="file_count", value=len(files)),
        EvidenceItem(source_type="v0_aggregate", source_id="transactions", metric="transaction_count", value=total_transactions),
        EvidenceItem(source_type="v0_aggregate", source_id="transactions", metric="total_cost", value=round(total_cost, 2), unit="INR"),
        EvidenceItem(source_type="v0_aggregate", source_id="buy_transactions", metric="sum_quantity_mw", value=round(total_quantity, 4), unit="MW-block sum"),
        EvidenceItem(source_type="v0_aggregate", source_id="buy_transactions", metric="average_rate", value=round(avg_rate, 2), unit="INR/MWh"),
        EvidenceItem(source_type="v0_aggregate", source_id="dor_transactions", metric="sum_quantity_mw", value=round(dor_quantity, 4), unit="MW-block sum"),
        EvidenceItem(source_type="v0_aggregate", source_id="sch_transactions", metric="sum_scheduled_quantity", value=round(sch_quantity, 4), unit="MW-block sum"),
    ]
    metrics = [
        ExplanationMetric(name="Files", value=len(files)),
        ExplanationMetric(name="Transactions", value=total_transactions),
        ExplanationMetric(name="Total cost", value=round(total_cost, 2), unit="INR"),
        ExplanationMetric(name="Average rate", value=round(avg_rate, 2), unit="INR/MWh"),
        ExplanationMetric(name="Buy intervals", value=buy_count),
        ExplanationMetric(name="Scheduling intervals", value=scheduling_count),
        ExplanationMetric(name="DOR quantity field sum", value=round(dor_quantity, 4), unit="MW-block sum"),
        ExplanationMetric(name="SCH quantity field sum", value=round(sch_quantity, 4), unit="MW-block sum"),
        ExplanationMetric(name="DOR minus SCH field sum", value=round(schedule_variance, 4), unit="MW-block sum"),
    ]
    limitations = [
        "This explanation uses existing V0 records and does not forecast future demand or IEX price.",
        "V0 files are not yet automatically linked to immutable SourceArtifact records.",
        "Cost fields reflect current parser/calculation semantics and require domain validation before trading decisions.",
        "Summed 15-minute MW fields are labeled MW-block sums; conversion to MWh requires approved interval semantics.",
    ]
    output = {
        "summary": summary,
        "metrics": [item.model_dump(mode="json") for item in metrics],
        "report_counts": dict(report_counts),
    }
    audit = create_audit_event(
        db,
        AIExecutionAuditCreate(
            correlation_id=request.correlation_id,
            client_id=request.client_id,
            portfolio_id=request.portfolio_id,
            actor_type="agent",
            actor_id="market-explanation-agent",
            agent_id="market-explanation",
            agent_version="1.0.0",
            capability="market.explain",
            input_references=[{"source_type": "v0_scope", "start_date": str(request.start_date), "end_date": str(request.end_date)}],
            tool_calls=[{"tool": "scoped_market_aggregates", "safety": "read_only"}],
            output_payload=output,
            confidence=confidence,
            status="requires_review" if review else "completed",
            limitations=limitations,
        ),
    )
    create_decision(
        db,
        DecisionRecordCreate(
            audit_event_id=audit.id,
            client_id=request.client_id,
            portfolio_id=request.portfolio_id,
            decision_type="market_explanation",
            title="Market data explanation",
            summary=summary,
            rationale=["All metrics were calculated from tenant-scoped V0 files and transactions."],
            evidence=evidence,
            alternatives=["Change the date/portfolio scope", "Run data quality analysis before interpretation"],
            limitations=limitations,
            confidence=confidence,
            human_review_required=review,
        ),
    )
    return MarketExplanationResponse(
        explanation_id=audit.id,
        client_id=request.client_id,
        portfolio_id=request.portfolio_id,
        question=request.question,
        answer=summary,
        summary=summary,
        metrics=metrics,
        evidence=evidence,
        confidence=confidence,
        limitations=limitations,
        data_classification="unknown-v0-lineage",
        engine=provider.provider_id,
        human_review_required=review,
    )
