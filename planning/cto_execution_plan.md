# CTO Execution Plan

## Purpose

This is the working CTO plan for turning the Power Trading application into a reliable SaaS-grade procurement optimization platform.

The plan should be reviewed and updated after each milestone. It is intentionally practical: stabilize the database foundation first, validate dashboards with mock data, then build the solar/IEX/TNEB planning engine and AI forecasting layer.

## Product Direction

```text
Power Trading Application
  -> SaaS platform for power procurement optimization
  -> Agentic-first operating model
  -> Helps clients reduce electricity cost
  -> Uses actual DOR/SCH data first
  -> Adds solar banking, forecasting, and trading recommendations later
```

## Agentic Operating Model

From day one, the company should be designed with an agentic AI mindset.

The goal is not to hire large teams for repetitive operations. The goal is to build agents that perform the repetitive work that BI analysts, data operators, and junior developers would normally do.

Humans should remain as specialists, reviewers, domain experts, and escalation owners.

```text
Human specialists:
  - Define business rules
  - Review exceptions
  - Approve sensitive actions
  - Improve strategy
  - Handle client relationships

Agents:
  - Fetch client emails
  - Detect attached DOR/SCH files
  - Validate file naming and completeness
  - Upload files
  - Parse and normalize data
  - Run data quality checks
  - Create dashboard-ready metrics
  - Detect anomalies
  - Generate reports
  - Notify humans only when needed
```

## Agent Architecture Vision

```text
Client Email Inbox
  -> Email Ingestion Agent
  -> Attachment Classification Agent
  -> File Validation Agent
  -> Upload And Parser Agent
  -> Data Quality Agent
  -> Dashboard Analysis Agent
  -> Procurement Recommendation Agent
  -> Human Review / Approval only for exceptions
```

Each agent must be observable and auditable.

For every automated action, the system should know:

- Which agent performed the action
- Which file/email/data triggered it
- What decision was made
- What confidence score was used
- Whether human review was required
- What output was written to the database

## CTO Principles

```text
1. Actual data and planning data must remain separate.
2. Raw uploads should be preserved.
3. Calculated data should be reproducible.
4. Forecasts and recommendations must be versioned.
5. Database changes must go through migrations.
6. Production data must be protected with backups and access controls.
7. Every dashboard number should be traceable back to source files.
8. Repetitive operational work should be delegated to agents by default.
9. Human review should be exception-based, not process-based.
10. Agents must be auditable, observable, and permission-controlled.
```

## Phase 0: Current Workspace Stabilization

Goal:

```text
Make the current V2 branch stable enough to become the working base.
```

Status:

```text
In progress
```

Completed:

- Identified V2 as the working branch.
- Aligned mock generator, parser output, and current data models.
- Generated 180 parser-compatible mock Excel reports.
- Created strategy and data model architecture artifacts.

Remaining:

- Review current changed files.
- Decide what should be committed.
- Keep unrelated old/generated clutter out of the main product path.

Exit Criteria:

```text
Clean working branch with approved architecture docs and mock data workflow.
```

## Phase 1: Database Foundation

Goal:

```text
Create a reliable PostgreSQL-backed foundation for actual uploaded data.
```

Tasks:

- Confirm Railway PostgreSQL app/database exists.
- Confirm `DATABASE_URL` points to the correct PostgreSQL instance.
- Create dev/staging/prod environment naming discipline.
- Add migration workflow, preferably Alembic.
- Generate initial migration from current models.
- Apply schema to staging PostgreSQL.
- Verify tables and relationships.

Current tables:

- `clients`
- `portfolios`
- `daily_files`
- `transactions`
- `monthly_calculations`
- `energy_schedule_months`
- `energy_schedule_days`

Exit Criteria:

```text
PostgreSQL schema exists, is migration-controlled, and can be inspected reliably.
```

## Phase 2: Mock Data Load And Validation

Goal:

```text
Load realistic mock data into PostgreSQL and verify that dashboards have usable data.
```

Tasks:

- Upload generated mock reports from `Data/mock_reports`.
- Validate row counts:
  - clients
  - portfolios
  - daily_files
  - transactions
  - energy_schedule tables
- Confirm report type counts:
  - DOR-GDAM
  - DOR-DAM
  - DOR-RTM
  - SCH-GDAM
  - SCH-DAM
  - SCH-RTM
- Validate 96 time slots per file.
- Confirm dashboard APIs return expected values.

Exit Criteria:

```text
Dashboard can run from PostgreSQL mock data without parser/model mismatch.
```

## Phase 3: Dashboard And Actuals Layer

Goal:

```text
Make the dashboard trustworthy for historical/actual data.
```

Tasks:

- Validate upload flow.
- Validate actual file replacement behavior.
- Show market-wise DOR/SCH status per day.
- Show missing file warnings.
- Show cost and schedule metrics.
- Add drill-down from dashboard number to source file/time slot.
- Design dashboard data flow so agents can generate the same insights automatically.

Exit Criteria:

```text
User can upload actual files and confidently inspect what happened.
```

## Phase 3A: Agentic Data Operations

Goal:

```text
Automate the BI/data-operations workflow using agents.
```

Agents:

- Email Ingestion Agent
- Attachment Classification Agent
- File Validation Agent
- Upload And Parser Agent
- Data Quality Agent
- Dashboard Analysis Agent
- Notification Agent

Tasks:

- Define allowed inbox/source rules.
- Define expected email/file patterns.
- Detect DOR/SCH attachments automatically.
- Validate client, portfolio, date, report type, and completeness.
- Upload files into the existing pipeline.
- Run parser checks and row-count checks.
- Produce dashboard-ready summaries.
- Notify humans only for missing files, parse failures, unusual values, or approval-required actions.

Exit Criteria:

```text
Routine client data intake and dashboard preparation can be performed by agents with full audit logs.
```

## Phase 4: Enterprise Database Controls

Goal:

```text
Make the system safe enough for SaaS operation.
```

Tasks:

- Add migration discipline.
- Add backup and restore process.
- Add audit fields:
  - source_email_id
  - source_attachment_id
  - agent_run_id
  - agent_name
  - agent_action
  - confidence_score
  - human_review_status
  - uploaded_by
  - uploaded_at
  - parser_version
  - calculation_version
  - forecast_model_version
  - recommendation_version
- Add tenant isolation checks.
- Add data retention policy.
- Add access roles:
  - app runtime
  - admin
  - readonly/analytics
- Add production safety rules.
- Add agent permission boundaries.
- Add agent run logs.
- Add exception queues for human specialists.

Exit Criteria:

```text
Database can support real client data with auditability, backups, and controlled access.
```

## Phase 5: Solar Bank And Planning Data Model

Goal:

```text
Add the missing business layer for monthly solar banking and procurement planning.
```

Proposed tables:

- `solar_banks`
- `solar_bank_entries`
- `demand_forecasts`
- `iex_price_forecasts`
- `procurement_plans`
- `procurement_plan_timeslots`

Tasks:

- Finalize solar bank rules.
- Define how solar is shared across portfolios.
- Define monthly expiry logic.
- Add forecast storage.
- Add procurement plan storage.
- Keep actual data separate from planned data.

Exit Criteria:

```text
Database can represent solar balance, forecasts, and daily procurement recommendations.
```

## Phase 6: Optimization Engine

Goal:

```text
Recommend the lowest-cost daily source mix.
```

Inputs:

- Demand forecast
- IEX price forecast
- Remaining solar bank
- Days left before solar expiry
- TNEB/Grid tariff
- Historical DOR/SCH actuals
- Agent-generated data quality signals

Outputs:

- Recommended IEX quantity
- Recommended solar usage
- Expected TNEB/Grid fallback
- Expected cost
- Expected savings
- Risk warning
- Explanation for human review

Exit Criteria:

```text
System can recommend a daily procurement plan and explain the reasoning.
```

## Phase 7: AI Forecasting And Agentic Decision Support

Goal:

```text
Predict next-day demand and IEX price to improve procurement decisions.
```

Tasks:

- Build baseline non-AI forecasting first.
- Add model versioning.
- Track prediction accuracy.
- Compare recommended plan vs actual outcome.
- Introduce AI models only after data quality is strong.
- Use agents to monitor forecast performance and flag drift.
- Use agents to prepare daily trading recommendations for specialist approval.

Exit Criteria:

```text
Forecasts and agent-generated recommendations improve daily buying decisions and can be audited against actual outcomes.
```

## Review Cadence

After every phase, review:

```text
1. What was completed?
2. What was validated?
3. What changed in the database?
4. What risks remain?
5. What should be done next?
```

## Immediate Next Step

```text
Phase 1: Confirm and stabilize PostgreSQL foundation.
```

Recommended next actions:

1. Confirm Railway PostgreSQL connection.
2. Inspect existing remote schema.
3. Decide migration tool setup.
4. Apply current schema to staging database.
5. Load mock data only after schema is confirmed.
