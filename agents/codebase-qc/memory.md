# Codebase QC Memory

This file stores concise, stable lessons from prior QC work. It is not a full log.

## 2026-07-11

- Production Railway app uses `Dockerfile` through `railway.json`.
- Legacy deployment configs were archived under `archive/legacy/deployment/`.
- Active frontend is `frontend-react/`.
- Legacy static frontend and duplicate packaged app were archived under `archive/legacy/apps/`.
- Root was reduced to production entrypoint files.
- Runtime artifacts are ignored/untracked:
  - `*.db`
  - `*.pid`
  - `*.zip`
  - logs
  - generated Excel/CSV files
  - `node_modules`
  - `dist`
- Production PostgreSQL data baseline after successful connection:
  - clients: 1
  - transactions: 17280
  - energy_schedule_months: 1
  - energy_schedule_days: 30
- Dashboard default was changed to show all data by default because mock data is January 2026.
- Railway PostgreSQL password should be rotated before serious production use because credentials appeared during setup conversation.

## Known follow-ups

- Update root `README.md` for the cleaned structure.
- Add non-hardcoded admin JWT secret.
- Decide when `archive/legacy/` can be deleted permanently.
- Add richer agent memory tables only after file-based registry proves useful.
