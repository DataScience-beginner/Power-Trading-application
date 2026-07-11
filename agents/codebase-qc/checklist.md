# Codebase QC Checklist

Use this checklist before committing cleanup, refactor, deployment, or structure changes.

## Git hygiene

```bash
git status --short
git diff --stat
git ls-files '.env' '.env.*' '*.db' '*.pid' '*.log' '*.zip' '**/node_modules/*' 'frontend-react/dist/*'
```

Expected:

- no tracked secrets;
- no tracked runtime DB/PID/log/ZIP files;
- no tracked dependency/build folders;
- `.env.example` is allowed.

## Root hygiene

Root should remain close to:

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

If a tracked root file appears, justify it or move it.

## Folder ownership

```text
api/                 FastAPI app
backend/             AI/weather support modules
database/            DB config/models/services
frontend-react/      active frontend
parsers/             report parsers
schemas/             shared schemas
scripts/             operational scripts
tests/               tests
docs/                product/architecture docs
planning/            plans/audits
agents/              agent registry/packages
archive/legacy/      old files preserved for reference
```

## Validation

For Python/backend/script changes:

```bash
python -m compileall -q api database parsers backend scripts tests
```

For frontend changes:

```bash
cd frontend-react
npm run build
```

For production/API-sensitive changes:

Check:

```text
/api/health
/api/clients
/api/analytics/summary
/api/energy-schedule/months
```

## Archive-first rule

Before deleting:

- confirm references;
- check deployment/build paths;
- move to `archive/legacy/`;
- validate;
- commit;
- delete later only after stable review.

## Commit summary

Every QC commit should say:

- category of cleanup;
- validation performed;
- remaining follow-ups.
