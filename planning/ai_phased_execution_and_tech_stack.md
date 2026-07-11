# AI Phased Execution Plan and Technology Stack

## Delivery sequence

| Phase | Indicative duration | Main output | Gate |
|---|---:|---|---|
| 0. Foundation | 2-3 weeks | Data contracts, lineage, audit and tenant authorization | Traceability and isolation tests |
| 1. Read-only AI | 3-4 weeks | Data Quality Agent, explanations and chatbot | Evaluation set, prompt-injection and authorization tests |
| 2. Forecasting | 6-8 weeks | Demand, solar and IEX forecasts | Backtest and monitoring thresholds |
| 3. Optimization | 6-8 weeks | Solar/IEX/TNEB procurement recommendations | Feasibility, replay and savings backtests |
| 4. Agentic operations | 6-10 weeks | Email-to-dashboard and approval workflows | Idempotency, recovery and audit tests |
| 5. Controlled trading | After governance approval | Market submission adapters | Dual approval, limits, reconciliation and kill switch |

Durations are planning ranges and should be revised after Phase 0 discovery.

## Frontend stack

- React + TypeScript for the existing SaaS application.
- Material UI for accessible enterprise components.
- Existing chart library for market and forecast visualization; standardize one library rather than adding duplicates.
- TanStack Query for server state, caching, retries and request lifecycle.
- React Hook Form + schema validation for upload and approval workflows.
- AI components: evidence panel, confidence band, recommendation comparison, feedback, approval timeline, and audit drawer.
- Server-Sent Events initially for long-running agent progress; WebSockets only when bidirectional real-time control is required.

## Backend and data stack

- FastAPI + Pydantic for typed, documented agent-safe tools.
- SQLAlchemy + PostgreSQL as the transactional system of record.
- Alembic for migrations.
- PostgreSQL row-level tenant controls or rigorously enforced tenant-scoped services.
- Object storage for immutable raw uploads; PostgreSQL stores metadata and lineage.
- Redis for bounded queues, locks, short-lived cache and rate limits when operational scale requires it.
- A worker system such as Celery, Dramatiq, or Arq selected during Phase 1; do not run long AI jobs in web requests.
- MLflow or an equivalent registry for model versions, metrics and promotion.
- Pandas/Polars and scikit-learn/lightGBM/XGBoost for baselines; specialized time-series models only after benchmarks.
- OR-Tools or Pyomo for constraint-aware procurement optimization.
- OpenTelemetry plus structured logs and metrics for API, model and agent observability.

## AI integration pattern

- Provider-neutral `AIProvider` interface rather than model calls inside routers.
- Prompt templates versioned outside route handlers.
- Tool registry generated from approved application capabilities.
- Retrieval restricted by tenant, portfolio, date range and user role.
- Evaluation datasets versioned for classification, extraction, explanation and recommendation quality.
- No vector database in Phase 0 unless document retrieval proves a real need; structured energy data remains in PostgreSQL.

## First implementation epic

Build the Data Quality and Market Explanation layer:

1. Define Pydantic request/response contracts.
2. Add read-only quality and explanation services.
3. Register endpoints in `api/endpoint_registry.yaml`.
4. Add deterministic rules before LLM explanations.
5. Add client-scoped evidence retrieval and audit events.
6. Add UI findings, evidence, confidence and feedback panels.
7. Create evaluation fixtures and rigorous tests.

This epic produces immediate value and creates the trusted foundation for forecasts and procurement recommendations.
