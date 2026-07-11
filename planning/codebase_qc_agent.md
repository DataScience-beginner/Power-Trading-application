# Codebase QC Agent

The Codebase QC Agent is the first internal agent for this project.

## Purpose

The QC Agent acts like a CTO/codebase guardian. Its job is to keep the repository production-ready before feature work continues.

## Responsibilities

- Enforce root-folder discipline.
- Prevent secrets and generated artifacts from entering Git.
- Keep deployment fast and deterministic.
- Keep scripts organized by purpose.
- Ensure old experiments are archived, not mixed with active code.
- Require validation before commits.
- Maintain a clear distinction between:
  - active source;
  - operational scripts;
  - tests;
  - docs;
  - planning;
  - legacy/archive.

## Current production structure

```text
api/                 FastAPI backend
backend/             AI/weather support modules
database/            SQLAlchemy models/config/services
frontend-react/      Active React UI
parsers/             DOR/SCH parsers
schemas/             Shared schema definitions
scripts/             Operational scripts
tests/               Test suite
docs/                Product/architecture docs
planning/            CTO plans and audits
archive/legacy/      Historical files, old app copies, old scripts
```

## Current root standard

Root should stay close to:

```text
AGENTS.md
README.md
Dockerfile
railway.json
requirements.txt
.dockerignore
.gitignore
.env.example
LICENSE
```

If a new root file appears, QC should challenge it.

## QC gates

### Gate 1 — Git hygiene

```bash
git status --short
git ls-files '.env' '.env.*' '*.db' '*.pid' '*.log' '*.zip' '**/node_modules/*' 'frontend-react/dist/*'
```

No secrets/runtime/build artifacts should be tracked.

### Gate 2 — Python sanity

```bash
python -m compileall -q api database parsers backend scripts tests
```

### Gate 3 — Frontend sanity

```bash
cd frontend-react
npm run build
```

### Gate 4 — Production API sanity

Check:

```text
/api/health
/api/clients
/api/analytics/summary
/api/energy-schedule/months
```

Expected production data baseline:

```text
clients: 1
transactions: 17280
energy_schedule_months: 1
energy_schedule_days: 30
```

## Cleanup doctrine

1. Move first.
2. Validate.
3. Commit.
4. Observe production.
5. Delete later only when safe.

## Current known follow-ups

- Update `README.md` to reflect the cleaned repo structure.
- Decide when `archive/legacy/` can be removed permanently.
- Consider rotating Railway PostgreSQL password because credentials appeared during setup.
- Add proper secret management and non-hardcoded admin JWT secret before serious production use.
