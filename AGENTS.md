# Codebase QC Agent Rules

This repository uses a strict Quality Controller agent mindset. Any AI agent or developer working here must follow these rules before changing, moving, deleting, or deploying code.

## Agent registry

Operational agent definitions live under:

```text
agents/
```

Always check:

```text
agents/registry.yaml
```

If the task matches a registered agent trigger, load that agent package before acting.

Current active agents:

```text
agents/codebase-qc/
agents/testing-qa/
```

## Mission

Keep the Power Trading application production-ready, lean, secure, and understandable.

The QC agent protects:

- production stability;
- data safety;
- secrets hygiene;
- clean repository structure;
- deployment speed;
- developer/agent clarity.

## Non-negotiable rules

1. Do not commit secrets.
   - Never commit `.env`, `.env.*`, database URLs, passwords, API keys, Railway tokens, private keys, or local credentials.
   - Use `.env.example` for placeholders only.

2. Do not commit runtime/generated artifacts.
   - Never commit `.db`, `.pid`, `.log`, `.zip`, `node_modules`, `dist`, generated Excel/CSV files, cache folders, or `__pycache__`.

3. Keep the root boring.
   - Root should contain only project entrypoints and deployment configuration.
   - Allowed root files are generally:
     - `README.md`
     - `Dockerfile`
     - `railway.json`
     - `requirements.txt`
     - `.gitignore`
     - `.dockerignore`
     - `.env.example`
     - `LICENSE`
     - `AGENTS.md`

4. Put scripts in `scripts/`.
   - Data generation: `scripts/data_generation/`
   - Ingestion/upload: `scripts/ingestion/`
   - Database ops: `scripts/db/`
   - Energy schedule ops: `scripts/energy_schedule/`
   - Diagnostics: `scripts/diagnostics/`
   - Templates: `scripts/templates/`

5. Put tests in `tests/`.
   - Test files should not live in root.
   - The default pre-commit gate is `python scripts/quality/golden_test.py --mode standard`.
   - Use the Testing QA Agent to choose smoke, standard, or rigorous depth.

6. Keep only one active app copy.
   - Active frontend: `frontend-react/`
   - Active backend/API: `api/`, `database/`, `parsers/`, `backend/`
   - Old copies belong under `archive/legacy/`, not root.

7. Do not delete first; archive first.
   - If a file may contain old knowledge, move it to `archive/legacy/`.
   - Delete only after a stable review period.

8. Update references when moving files.
   - Search for old paths after every move.
   - Update `api/main.py`, docs, scripts, Docker/deploy configs, and tests as needed.

9. Validate in proportion to risk.
   - Frontend changes: run `npm run build` in `frontend-react/`.
   - Python/backend/script changes: run `python -m compileall -q api database parsers backend scripts tests`.
   - API/deploy changes: smoke test `/api/health`, `/api/clients`, and relevant endpoints.

10. Protect production deployment.
    - Railway uses `Dockerfile` + `railway.json`.
    - Do not introduce competing deployment config unless intentionally adopted.
    - Keep `.dockerignore` strict so deploy context stays small.

## Required pre-commit QC checklist

Before committing, run:

```bash
git status --short
git diff --stat
git ls-files '.env' '.env.*' '*.db' '*.pid' '*.log' '*.zip' '**/node_modules/*' 'frontend-react/dist/*'
```

Expected result for the last command: no tracked files, except allowed examples like `.env.example`.

For code changes, run the golden gate:

```bash
python scripts/quality/golden_test.py --mode standard
```

For risky releases, API refactors, database/model changes, parser changes, calculation changes, or chatbot/tool endpoints, run:

```bash
python scripts/quality/golden_test.py --mode rigorous
```

If rigorous mode reports missing test dependencies, install the development dependencies first:

```bash
pip install -r requirements-dev.txt
```

The golden gate includes the relevant checks:

```bash
python -m compileall -q api database parsers backend scripts tests
cd frontend-react && npm run build
```

If a check is skipped or cannot run, the checkpoint summary must say why.

## Required PR / checkpoint summary

Every meaningful cleanup or feature commit should state:

- What changed.
- Why it changed.
- What was intentionally not changed.
- Validation performed.
- Any risk or follow-up.

## Production data rule

Mock/demo data should be generated intentionally and loaded through controlled scripts or API flows.

Never rely on local SQLite state for production behavior.

Production Railway app must use PostgreSQL through `DATABASE_URL`.

## Agent behavior rule

If an agent is unsure whether a file is active, it must:

1. search references;
2. inspect deployment/build paths;
3. archive instead of delete;
4. report the decision.

No silent destructive cleanup.
