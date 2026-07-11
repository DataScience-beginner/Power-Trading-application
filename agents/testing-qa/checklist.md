# Testing QA Checklist

## Always check

- No tracked secrets or generated artifacts.
- Python files compile.
- Golden static contracts pass.
- Frontend builds when frontend or API response behavior changes.

## Golden command

```bash
python scripts/quality/golden_test.py --mode standard
```

## Smoke command

```bash
python scripts/quality/golden_test.py --mode smoke
```

## Rigorous command

```bash
python scripts/quality/golden_test.py --mode rigorous
```

## API contract checklist

Core endpoints that must remain discoverable:

- `/api/health`
- `/api/clients`
- `/api/analytics/summary`
- `/api/energy-schedule/months`
- `/api/energy-schedule/days`
- `/api/calculate/energy-schedule`
- `/api/reports/daily-trading/pdf`
- `/api/reports/daily-trading/excel`

## Energy schedule checklist

Validate that the codebase still contains:

- energy schedule month model;
- energy schedule day model;
- schedule rebuild script;
- calculation API endpoint;
- frontend energy schedule page;
- energy schedule API client methods/types.

## Chatbot readiness checklist

Before adding chatbot endpoints, confirm:

- endpoint returns structured JSON;
- endpoint is read-only unless explicitly approved;
- output is explainable in business language;
- endpoint does not expose credentials;
- AI recommendation actions are auditable.

