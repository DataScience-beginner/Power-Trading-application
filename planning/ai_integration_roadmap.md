# Innowatt AI Integration Roadmap

## Product objective

Forecast demand, solar availability, and IEX prices; recommend the lowest-risk, lowest-cost Solar/IEX/TNEB mix; explain every recommendation; and automate routine data operations with human approval for consequential actions.

## Reference architecture

```text
Files / Email / Meters / Weather / IEX / Tariffs
                         |
              Ingestion and validation
                         |
       Governed energy data + feature platform
                         |
        Demand + Solar + Price forecasting
                         |
          Constraint-aware optimization
                         |
 Recommendation + confidence + explanation
                         |
 Dashboard / Chat / Alerts / Approval workflow
                         |
             Controlled market execution
```

## AI capability layers

1. Predictive AI estimates demand, solar generation, market price, anomalies, and uncertainty.
2. Prescriptive optimization selects quantities under business and market constraints.
3. Generative AI explains results and invokes approved, structured application tools.
4. Agentic automation performs bounded workflows with permissions, idempotency, audit, and escalation.

## Phase AI-0: Trust foundation

Implementation status: foundation implemented on 2026-07-11; production migration and SaaS JWT/RBAC promotion remain deployment follow-ups.

Deliver:

- canonical client/portfolio/site/meter/block data contracts;
- source-file lineage and data-quality status;
- model, prompt and recommendation versioning;
- AI audit events and feedback capture;
- tenant-safe authorization for every AI tool.

Exit metric: every displayed or AI-referenced number is traceable to source and client scope.

Implemented foundation:

- additive canonical entities with versioned dynamic attributes;
- immutable source-artifact lineage and synthetic-data marking;
- processing-run provenance;
- effective-dated and human-approved business-rule versions;
- AI execution audit envelopes;
- evidence-backed structured decisions and deterministic human narratives;
- agent-readable capability catalog and endpoint registry;
- fail-closed machine-to-machine authentication for protected operations;
- isolated deterministic tests that never write to Railway.

## Phase AI-1: Read-only intelligence

Implementation status: deterministic AI-1 implementation completed locally; Railway migration, service credential, and deployment remain final promotion steps.

Deliver:

- upload classification and data-quality agent;
- missing/duplicate/abnormal block detection;
- market snapshot explanation;
- daily portfolio narrative and report draft;
- read-only chatbot over approved APIs.

Exit metric: at least 90% of seeded file defects detected; zero cross-client data exposure; all answers cite internal evidence.

Implemented foundation:

- versioned dynamic QualityPolicy and deterministic rule engine;
- persisted quality runs and evidence-backed findings;
- scoped market aggregate explanation with audit and decision records;
- bounded assistant intents with unsupported-question refusal;
- specialist AI Insights UI with session-only credential handling;
- Data Quality and Market Insight governed agents;
- isolated tests with no Railway writes.

## Phase AI-2: Forecasting

## Phase AI-1.5: Authenticated conversational assistant

Implementation scope:

- database-backed SaaS users and JWT authentication;
- admin/client roles and portfolio restrictions;
- fixed tenant-scoped conversation storage;
- approved quality and market tools;
- prompt-injection and consequential-action refusal;
- optional Groq free-tier narration with deterministic fallback;
- global chatbot UI with evidence, confidence, provider, and safety status.

Deliver:

- 15-minute demand forecast;
- daily/monthly solar forecast;
- next-day IEX price forecast with quantiles;
- forecast-versus-actual monitoring;
- baseline, champion and challenger model registry.

Exit metric: models beat agreed seasonal/naive baselines and report accuracy by client, portfolio, horizon, and block.

## Phase AI-3: Procurement optimizer

Objective:

```text
Minimize solar expiry cost + IEX cost + TNEB cost
       + deviation penalties + forecast risk
```

Constraints include demand balance, solar bank and expiry, IEX validity, portfolio allocation, contracted demand, market rules, and user risk limits.

Exit metric: recommendations are reproducible, feasible, explainable, and outperform the approved baseline in backtests.

## Phase AI-4: Controlled autonomy

Deliver:

- email/attachment intake;
- automatic validation, ingestion and dashboard refresh;
- recommendation preparation and approval workflow;
- later, market submission only behind explicit permissions and kill switches.

Exit metric: routine workflows complete without manual handling while every mutation remains approved, idempotent, and auditable.

## AI safety contract

- The LLM never calculates authoritative schedules itself.
- Forecast and optimization services return structured, versioned results.
- Mutating tools require explicit permission and approval policy.
- Every output records tenant, actor, source data, model, prompt/template, confidence, action, and outcome.
- Low confidence, missing data, policy conflicts, and unusual cost exposure escalate to a specialist.
