"""Deterministic AI-1 data-quality engine over the current V0 compatibility model."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.schemas.ai_insights import QualityAnalysisRequest, QualityFindingResponse, QualityRunResponse
from api.services.ai_foundation_service import validate_scope
from database.ai_insights_models import DataQualityFinding, DataQualityRun
from database.models import DailyFile, Portfolio, Transaction


ENGINE_VERSION = "1.0.0"


def utc_now() -> datetime:
    """Return naive UTC for current database timestamp compatibility."""
    return datetime.now(UTC).replace(tzinfo=None)


@dataclass
class FindingCandidate:
    """Internal finding before persistence assigns identifiers."""

    rule_id: str
    severity: str
    category: str
    title: str
    description: str
    evidence: list[dict[str, Any]]
    recommended_action: str
    portfolio_id: int | None = None
    daily_file_id: int | None = None
    confidence: float = 1.0


def finding(
    rule_id: str,
    severity: str,
    category: str,
    title: str,
    description: str,
    evidence: list[dict[str, Any]],
    recommended_action: str,
    portfolio_id: int | None = None,
    daily_file_id: int | None = None,
) -> FindingCandidate:
    """Create a concise deterministic finding candidate."""
    return FindingCandidate(
        rule_id=rule_id,
        severity=severity,
        category=category,
        title=title,
        description=description,
        evidence=evidence,
        recommended_action=recommended_action,
        portfolio_id=portfolio_id,
        daily_file_id=daily_file_id,
    )


def scoped_files(db: Session, request: QualityAnalysisRequest) -> list[DailyFile]:
    """Load files only from the explicitly validated client/date/portfolio scope."""
    query = db.query(DailyFile).join(Portfolio).filter(
        Portfolio.client_id == request.client_id,
        DailyFile.trading_date >= request.start_date,
        DailyFile.trading_date <= request.end_date,
    )
    if request.portfolio_id:
        query = query.filter(Portfolio.id == request.portfolio_id)
    return query.order_by(DailyFile.trading_date, DailyFile.id).all()


def evaluate_coverage(files: list[DailyFile], request: QualityAnalysisRequest) -> list[FindingCandidate]:
    """Evaluate dynamic report coverage and duplicate source classifications."""
    if not files:
        return [
            finding(
                "coverage.no_files",
                "high",
                "coverage",
                "No source files in scope",
                "No V0 source files were found for the requested client, portfolio, and date range.",
                [{"start_date": str(request.start_date), "end_date": str(request.end_date)}],
                "Confirm the selected scope and upload or ingest the expected source files.",
                request.portfolio_id,
            )
        ]

    findings: list[FindingCandidate] = []
    grouped: dict[tuple[int, Any], list[DailyFile]] = defaultdict(list)
    for file in files:
        grouped[(file.portfolio_id, file.trading_date)].append(file)

    expected = set(request.policy.expected_report_types)
    for (portfolio_id, trading_date), day_files in grouped.items():
        counts = Counter(file.report_type for file in day_files)
        missing = sorted(expected - set(counts))
        duplicates = sorted(report_type for report_type, count in counts.items() if count > 1)
        if missing:
            findings.append(
                finding(
                    "coverage.missing_report_types",
                    "high",
                    "coverage",
                    "Expected report types are missing",
                    f"{len(missing)} configured report types are absent for {trading_date}.",
                    [{"trading_date": str(trading_date), "missing_report_types": missing}],
                    "Verify source delivery and confirm whether the quality policy requires updating.",
                    portfolio_id,
                )
            )
        if duplicates:
            findings.append(
                finding(
                    "coverage.duplicate_report_types",
                    "medium",
                    "duplication",
                    "Duplicate report classifications detected",
                    f"Multiple files share the same configured report type for {trading_date}.",
                    [{"trading_date": str(trading_date), "duplicate_report_types": duplicates}],
                    "Review file lineage and mark the authoritative artifact or superseding version.",
                    portfolio_id,
                )
            )
    return findings


def evaluate_file_transactions(
    db: Session,
    files: list[DailyFile],
    request: QualityAnalysisRequest,
) -> tuple[list[FindingCandidate], int]:
    """Evaluate block completeness, duplicates, timestamps, quantities, and rates."""
    findings: list[FindingCandidate] = []
    transaction_total = 0
    for file in files:
        transactions = db.query(Transaction).filter(Transaction.daily_file_id == file.id).all()
        transaction_total += len(transactions)
        expected_blocks = request.policy.expected_blocks_per_file
        if len(transactions) != expected_blocks:
            severity = "high" if not transactions else "medium"
            findings.append(
                finding(
                    "interval.block_count",
                    severity,
                    "completeness",
                    "Unexpected interval block count",
                    f"File has {len(transactions)} blocks; policy expects {expected_blocks}.",
                    [{"actual_blocks": len(transactions), "expected_blocks": expected_blocks, "report_type": file.report_type}],
                    "Inspect parsing output and source completeness before using this file for analysis.",
                    file.portfolio_id,
                    file.id,
                )
            )

        slots = [txn.time_slot for txn in transactions if txn.time_slot]
        duplicate_slots = sorted(slot for slot, count in Counter(slots).items() if count > 1)
        if duplicate_slots:
            findings.append(
                finding(
                    "interval.duplicate_blocks",
                    "high",
                    "duplication",
                    "Duplicate time blocks detected",
                    f"File contains {len(duplicate_slots)} duplicated time-block labels.",
                    [{"duplicate_blocks": duplicate_slots[:20], "total_duplicate_labels": len(duplicate_slots)}],
                    "Stop downstream calculations and resolve duplicate source or parser rows.",
                    file.portfolio_id,
                    file.id,
                )
            )

        missing_time = sum(1 for txn in transactions if txn.time_block_start is None)
        if request.policy.require_time_block_start and missing_time:
            findings.append(
                finding(
                    "interval.missing_start_time",
                    "medium",
                    "schema",
                    "Canonical block timestamps are missing",
                    f"{missing_time} transactions do not have time_block_start.",
                    [{"missing_count": missing_time, "transaction_count": len(transactions)}],
                    "Normalize source time labels into canonical timestamps before AI/forecast use.",
                    file.portfolio_id,
                    file.id,
                )
            )

        negative_quantities = sum(1 for txn in transactions if (txn.quantity_mw or 0) < 0)
        if negative_quantities and not request.policy.allow_negative_quantity:
            findings.append(
                finding(
                    "value.negative_quantity",
                    "high",
                    "validity",
                    "Negative quantities violate the active policy",
                    f"{negative_quantities} transactions contain negative quantity_mw values.",
                    [{"negative_count": negative_quantities}],
                    "Confirm sign conventions and update the policy only after domain approval.",
                    file.portfolio_id,
                    file.id,
                )
            )

        invalid_rates = sum(1 for txn in transactions if (txn.rate_per_mwh or 0) < request.policy.minimum_rate)
        high_rates = sum(
            1
            for txn in transactions
            if request.policy.maximum_rate is not None and (txn.rate_per_mwh or 0) > request.policy.maximum_rate
        )
        if invalid_rates or high_rates:
            findings.append(
                finding(
                    "value.rate_threshold",
                    "medium",
                    "validity",
                    "Rates fall outside configured thresholds",
                    f"{invalid_rates} rates are below minimum and {high_rates} exceed maximum.",
                    [{"below_minimum": invalid_rates, "above_maximum": high_rates}],
                    "Review the values and the effective client/market threshold configuration.",
                    file.portfolio_id,
                    file.id,
                )
            )
    return findings, transaction_total


def run_quality_analysis(db: Session, request: QualityAnalysisRequest) -> QualityRunResponse:
    """Run, persist, and return deterministic findings without production-side correction."""
    validate_scope(db, request.client_id, request.portfolio_id)
    started_at = utc_now()
    files = scoped_files(db, request)
    candidates = evaluate_coverage(files, request)
    transaction_findings, transaction_total = evaluate_file_transactions(db, files, request)
    candidates.extend(transaction_findings)

    counts = Counter(item.severity for item in candidates)
    run = DataQualityRun(
        correlation_id=request.correlation_id,
        client_id=request.client_id,
        portfolio_id=request.portfolio_id,
        start_date=request.start_date,
        end_date=request.end_date,
        policy_version=request.policy.policy_version,
        policy_configuration=request.policy.model_dump(mode="json"),
        engine_version=ENGINE_VERSION,
        files_evaluated=len(files),
        transactions_evaluated=transaction_total,
        finding_counts=dict(counts),
        data_classification=request.data_classification,
        started_at=started_at,
        completed_at=utc_now(),
    )
    db.add(run)
    db.flush()

    records = []
    for item in candidates:
        record = DataQualityFinding(
            run_id=run.id,
            client_id=request.client_id,
            portfolio_id=item.portfolio_id,
            daily_file_id=item.daily_file_id,
            rule_id=item.rule_id,
            severity=item.severity,
            category=item.category,
            title=item.title,
            description=item.description,
            evidence=item.evidence,
            recommended_action=item.recommended_action,
            confidence=item.confidence,
        )
        db.add(record)
        records.append(record)
    db.commit()
    db.refresh(run)
    for record in records:
        db.refresh(record)

    limitations = [
        "V0 files are not yet automatically linked to AI-0 SourceArtifact lineage.",
        "Configured expectations are quality policy inputs and may change by client or market.",
        "Findings do not modify source data or authoritative schedules.",
    ]
    return QualityRunResponse(
        **{column.name: getattr(run, column.name) for column in DataQualityRun.__table__.columns},
        findings=[QualityFindingResponse.model_validate(record) for record in records],
        limitations=limitations,
    )


def latest_quality_summary(db: Session, client_id: int, portfolio_id: int | None) -> dict[str, int]:
    """Return severity counts from the latest run in the requested scope."""
    validate_scope(db, client_id, portfolio_id)
    query = db.query(DataQualityRun).filter(DataQualityRun.client_id == client_id)
    if portfolio_id is not None:
        query = query.filter(DataQualityRun.portfolio_id == portfolio_id)
    latest = query.order_by(DataQualityRun.started_at.desc()).first()
    return latest.finding_counts if latest else {}


def get_quality_run(db: Session, run_id: str, client_id: int) -> QualityRunResponse:
    """Retrieve a persisted run and findings only through mandatory client scope."""
    validate_scope(db, client_id, None)
    run = db.query(DataQualityRun).filter(
        DataQualityRun.id == run_id,
        DataQualityRun.client_id == client_id,
    ).first()
    if not run:
        raise HTTPException(status_code=404, detail="Quality run not found in client scope")
    records = db.query(DataQualityFinding).filter(DataQualityFinding.run_id == run.id).order_by(
        DataQualityFinding.severity,
        DataQualityFinding.detected_at,
    ).all()
    return QualityRunResponse(
        **{column.name: getattr(run, column.name) for column in DataQualityRun.__table__.columns},
        findings=[QualityFindingResponse.model_validate(record) for record in records],
        limitations=[
            "V0 files are not yet automatically linked to AI-0 SourceArtifact lineage.",
            "Findings are deterministic observations and do not correct production data.",
        ],
    )
