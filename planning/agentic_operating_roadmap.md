# Agentic Way of Working Roadmap

## Operating principle

Agents perform repeatable bounded work. Specialists own policy, domain rules, exceptions, client relationships, and approval of consequential actions.

## Agent workflow

```text
Trigger -> Classify -> Validate -> Plan -> Execute tool
        -> Verify -> Record audit -> Notify or escalate
```

## Initial agent portfolio

| Agent | Responsibility | Permission level | Human gate |
|---|---|---|---|
| Email Intake | Fetch approved messages and attachments | Read external, write intake queue | Unknown sender/file |
| File Classifier | Identify client, portfolio, date and report type | Read-only | Low confidence |
| Data Quality | Validate schema, blocks and anomalies | Read and create findings | Production correction |
| Upload/Parser | Invoke existing ingestion APIs idempotently | Controlled write | Failed or conflicting upload |
| Dashboard Analyst | Produce metrics and narratives | Read-only | Material unexplained anomaly |
| Forecast Monitor | Run and evaluate approved models | Controlled compute/write | Drift or poor accuracy |
| Procurement Advisor | Create recommendation scenarios | Read-only recommendation | Always before trade |
| Notification | Send approved summaries and escalations | Controlled outbound | Sensitive recipient/content |

## Enterprise control plane

Maintain a registry containing agent identity, owner, version, status, triggers, tools, data scope, permissions, model policy, budget, quality gates, escalation rules, and rollback procedure.

Every run records:

- correlation and tenant IDs;
- trigger and input references;
- tool calls and outputs;
- confidence and policy decisions;
- token/cost/latency metrics;
- approval and final outcome.

## Context and token efficiency

- Load registry and task-specific instructions, not the entire repository.
- Retrieve only relevant client/date/portfolio records.
- Use structured API responses and compact summaries.
- Cache deterministic parsing, features, forecasts, and approved knowledge by versioned key.
- Store durable facts in governed data stores; do not repeatedly place them in prompts.
- Use smaller models for classification/extraction and stronger models only for complex reasoning.

## Rollout

1. Shadow: agent observes and proposes; humans perform the work.
2. Assist: agent prepares outputs; humans approve each action.
3. Supervised automation: low-risk actions execute; exceptions escalate.
4. Bounded autonomy: approved workflows execute within limits and kill switches.

No agent advances a level without measured accuracy, security review, audit completeness, failure recovery, and named ownership.
