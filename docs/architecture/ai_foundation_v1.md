# AI Foundation V1

## Status

AI-0 additive compatibility foundation. The current trading tables and synthetic mock data remain first-cut inputs, not final domain truth.

## Why this exists

The application needs to accept changing clients, assets, market products, tariffs, rules, source formats, and AI models without adding hardcoded columns for every change. AI Foundation V1 adds versioned contracts around the existing application while preserving backward compatibility.

## Data flow

```text
Source file / email / API / meter feed
  -> SourceArtifact (checksum, schema, parser, synthetic status)
  -> ProcessingRun (agent/service/version/input/output/error)
  -> CanonicalEntity compatibility mapping
  -> Effective BusinessRuleVersion
  -> AIExecutionAudit
  -> DecisionRecord (structured evidence + deterministic human narrative)
```

## Dynamic model policy

- `CanonicalEntity.entity_type` is configurable; it is not a database enum.
- Type-specific values live in versioned `attributes` until a stable, frequently queried concept earns a dedicated normalized model.
- Rules use effective dates and versions so old calculations can be replayed.
- Raw source references and checksums are immutable.
- `is_synthetic` prevents mock data from silently becoming production truth.
- Existing V0 data is adapted incrementally; no destructive migration is performed.

## Agent contract

Agents discover capabilities through:

```text
GET /api/v1/ai-foundation/capabilities
```

Every controlled write requires:

- explicit client scope;
- typed Pydantic input;
- contract version;
- actor/agent identity where applicable;
- evidence or lineage references;
- clear safety and human-review metadata in the endpoint registry.

Client-sensitive reads and every controlled write also require the
`X-AI-Foundation-Key` header. The service fails closed when
`AI_FOUNDATION_API_KEY` is not configured. This service credential is an
initial machine-to-machine boundary; client JWT/RBAC integration remains the
required SaaS identity enhancement.

## Human decision contract

A decision contains title, summary, rationale, evidence, alternatives, limitations, confidence, status, and review requirement. The API creates a concise deterministic narrative from these structured facts. This narrative is explainable output, not hidden chain-of-thought and not an authoritative trading schedule.

## Deployment

The migration is additive. Before production promotion:

1. Back up PostgreSQL.
2. Apply `database/migrations/ai_foundation_v1.sql` in staging.
3. Run model and API integration tests.
4. Verify existing dashboards and APIs.
5. Apply in production during an approved deployment.

Application startup imports these models so new clean environments can create the tables. Production schema changes should still follow the reviewed migration path.

## Explicit limitations

- Client scope validation and fail-closed service authentication are implemented, but full client JWT/RBAC enforcement must be integrated before external clients use these endpoints.
- No LLM provider is connected in AI-0.
- No forecast, optimizer, schedule mutation, or trade execution is implemented.
- Current synthetic V0 data is useful only for workflow and defect testing.
