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

Deliver:

- canonical client/portfolio/site/meter/block data contracts;
- source-file lineage and data-quality status;
- model, prompt and recommendation versioning;
- AI audit events and feedback capture;
- tenant-safe authorization for every AI tool.

Exit metric: every displayed or AI-referenced number is traceable to source and client scope.

## Phase AI-1: Read-only intelligence

Deliver:

- upload classification and data-quality agent;
- missing/duplicate/abnormal block detection;
- market snapshot explanation;
- daily portfolio narrative and report draft;
- read-only chatbot over approved APIs.

Exit metric: at least 90% of seeded file defects detected; zero cross-client data exposure; all answers cite internal evidence.

## Phase AI-2: Forecasting

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
