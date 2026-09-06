# Testing Modes And Low-Token Development Workflow

Use the smallest validation mode that matches the risk of the change. Save rigorous checks for release-level confidence or risky backend/API/calculation work.

## Testing modes

| Mode | Use when | Commands | Notes |
|---|---|---|---|
| Tiny syntax check | Small Python/backend edit | `.venv/Scripts/python.exe -m compileall -q api database parsers backend scripts tests` | Fastest useful check. |
| Focused feature test | Excel calculation or one feature changed | `.venv/Scripts/python.exe -m pytest tests/test_energy_excel_calculation.py -q` | Prefer focused tests during iteration. |
| Backend confidence | Backend behavior changed across modules | `.venv/Scripts/python.exe -m pytest tests -q` | Run before a meaningful backend checkpoint. |
| E2E diagnostic | Upload/store/calculate workflow changed | `.venv/Scripts/python.exe scripts/diagnostics/verify_excel_calculation_e2e.py` | Keep output summarized; inspect full logs only on failure. |
| Standard gate | Normal pre-commit checkpoint | `.venv/Scripts/python.exe scripts/quality/golden_test.py --mode standard` | Default commit gate. |
| Rigorous gate | Release, deployment, DB/model/parser/calculation/API-risk checkpoint | `.venv/Scripts/python.exe scripts/quality/golden_test.py --mode rigorous` | Slow; includes frontend build and full test suite. |
| Frontend build | Frontend code changed, or final release proof needed | `cd frontend-react; npm.cmd run build` | Use `npm.cmd` on Windows PowerShell to avoid `npm.ps1` execution-policy errors. |

## Development loop

1. Search narrowly with `rg` before opening files.
2. Read only the function/class/range needed for the current decision.
3. Make small patches.
4. Run focused checks first.
5. Broaden validation only when focused checks pass or when the risk requires it.
6. Keep command output quiet with `-q` and summaries.
7. Do not run frontend build during backend-only loops unless preparing a checkpoint.

## Reporting format

Use compact checkpoint summaries:

- What changed.
- Why it changed.
- Validation mode used.
- Pass/fail result.
- Skipped checks and reason.
- Next safest step.

## Current repo notes

- Calculation/API/model/parser changes justify rigorous validation before final release or commit.
- During active Excel backend work, focused tests plus compile are enough for iteration.
- `npm run build` can take several minutes because it runs TypeScript and Vite across thousands of modules.
- Rigorous gate may time out in frontend build on a slow machine even when `npm.cmd run build` passes separately.
