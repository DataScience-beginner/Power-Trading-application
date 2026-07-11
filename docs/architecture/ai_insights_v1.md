# AI Insights V1

## Purpose

AI-1 adds useful intelligence without requiring an external model provider: deterministic data-quality analysis, evidence-backed market explanations, and a bounded assistant. It builds on AI Foundation V1 and does not treat V0 tables or mock data as final truth.

## Architecture

```text
Specialist / AI Insights UI
  -> service credential + client/date scope
  -> typed AI Insights API
       -> Data Quality Agent -> dynamic QualityPolicy -> findings
       -> Market Insight Agent -> scoped aggregates -> evidence/explanation
       -> Assistant router -> approved intents/tools only
  -> AIExecutionAudit + DecisionRecord
  -> human-readable response with confidence and limitations
```

## Data-quality rules

The first engine supports configurable:

- expected report types by portfolio/day;
- duplicate report classifications;
- expected interval blocks per file;
- duplicate time-block labels;
- required canonical block timestamps;
- negative-quantity policy;
- minimum and optional maximum rate thresholds.

Defaults mirror the current first-cut workflow and are not permanent. Future domain-approved BusinessRuleVersion configurations can supply client, portfolio, jurisdiction, or market policies.

## Explanation boundary

The explanation service calculates only scoped counts, recorded quantities, costs, rates, and report composition. It records evidence and limitations. It does not infer future values or create an authoritative procurement decision.

Narratives use a provider-neutral `NarrativeProvider` contract. AI-1 selects the deterministic key-free provider. A future LLM adapter will receive only approved structured facts and cannot query the database or replace authoritative calculations.

## Assistant boundary

Supported intents are quality, coverage, recorded market cost, and schedule-data context. The assistant cannot execute user-supplied SQL or invoke mutating tools. Unsupported questions receive a refusal and suggested safe questions.

Prohibited forecast, prediction, correction, schedule-change, bid, and trade requests are rejected before informational keywords such as IEX, price, or schedule are considered. This prevents a consequential request from being misrouted as a harmless explanation.

## Frontend security

The current internal UI accepts the AI Foundation service key and stores it in `sessionStorage`, never source code or persistent local storage. Before external client release, replace this temporary specialist workflow with SaaS JWT/RBAC and server-side agent credentials.

## Deployment dependencies

Before Railway deployment:

1. Back up PostgreSQL.
2. Apply/review AI Foundation V1 and AI Insights V1 additive migrations.
3. Configure `AI_FOUNDATION_API_KEY` securely.
4. Deploy and smoke-test capabilities with a non-production client scope first.
5. Confirm existing dashboards remain unchanged.

No external LLM API key is required for AI-1.
