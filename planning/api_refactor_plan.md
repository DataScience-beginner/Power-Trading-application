# API Refactor Plan

## Goal

Refactor the current FastAPI backend into an enterprise, agent-friendly API structure without changing behavior.

The current `api/main.py` is over the QC limit and should not receive new feature logic.

## Current issue

```text
api/main.py: 2,597 lines
```

QC policy:

- target maximum: 1,000 lines per source file;
- temporary exception maximum: 1,500 lines with a refactor note;
- no new behavior should be added to files above 1,500 lines.

## Target structure

```text
api/
  main.py                 FastAPI app creation, middleware, router registration
  endpoint_registry.yaml  Machine-readable route ownership and chatbot/tool metadata
  routers/
    health.py
    admin.py
    workbook_auth.py
    workbooks.py
    uploads.py
    clients.py
    analytics.py
    energy_schedule.py
    energy_calculations.py
    reports.py
    ai.py
    web.py
  schemas/
    admin.py
    workbooks.py
    clients.py
    analytics.py
    energy_schedule.py
    reports.py
    ai.py
  services/
    analytics_service.py
    energy_schedule_service.py
    report_service.py
    assistant_service.py
```

## Enterprise API registry rule

The file [api/endpoint_registry.yaml](/workspaces/Power-Trading-application/api/endpoint_registry.yaml) is the planning registry for:

- agents;
- chatbot tools;
- QA tests;
- endpoint ownership;
- refactor sequencing;
- safety level.

FastAPI `/openapi.json` remains the runtime source of exact API schema.

The registry is the human/agent governance layer; OpenAPI is the runtime contract.

## Pydantic and documentation rule

Every new or refactored endpoint should have:

- Pydantic request model for body input;
- Pydantic response model for JSON output;
- `summary`;
- `description`;
- typed query/path parameters;
- clear service function call;
- no large business logic inside route function.

Example shape:

```python
@router.get(
    "/api/clients",
    response_model=list[ClientSummaryResponse],
    summary="List clients",
    description="Returns clients available to the current user for dashboard and assistant workflows.",
)
def list_clients(db: Session = Depends(get_db)) -> list[ClientSummaryResponse]:
    return client_service.list_clients(db)
```

## Refactor sequence

1. Add route registry and tests.
2. Extract `health` and static web routes first.
3. Extract read-only `clients` and `analytics`.
4. Extract `energy_schedule` read endpoints.
5. Extract energy calculation endpoints.
6. Extract reports.
7. Extract uploads and controlled-write endpoints.
8. Extract admin/auth last because security risk is higher.
9. Add assistant/chatbot endpoints only after read-only API contracts are stable.

## Testing rule

After every router extraction:

```bash
python scripts/quality/golden_test.py --mode rigorous
```

If endpoint behavior changes, add/adjust deterministic API contract tests.

