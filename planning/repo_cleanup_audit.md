# Repository Cleanup Audit

Date: 2026-07-11

## Current state

The application is now deployed and production data is visible. Before removing files, the repository should be cleaned in controlled phases.

Current tracked inventory:

- Total tracked files: 239
- Tracked root files: 112
- Root Python scripts: 56
- Root Markdown files: 29
- Active frontend: `frontend-react/`
- Active backend: `api/`, `database/`, `parsers/`, `backend/ai/`
- Deployment: `Dockerfile`, `railway.json`, `.dockerignore`

Current local-only modified file after the last push:

- `power_trading.db` — local SQLite runtime state. Do not commit.

## Confirmed active source areas

Keep these as first-class project folders:

```text
api/
backend/
database/
frontend-react/
parsers/
schemas/
docs/
planning/
```

Keep these root files:

```text
Dockerfile
railway.json
requirements.txt
.dockerignore
.gitignore
.env.example
README.md
LICENSE
```

## Files/folders that are probably legacy or archive

These should be reviewed before delete/move:

```text
frontend/                  # old static HTML UI; active UI is frontend-react
desktop-wpf/               # separate/old desktop concept
power_trading_package/     # packaged copy of older app source
PowerTradingDashboard_*.zip
```

Recommended action:

- Move to `archive/legacy/` first, then delete later after one stable sprint.
- Do not leave duplicate app source in root because it confuses deployment and code review.

## Root scripts audit

Root currently has 56 Python scripts. Most are one-off helpers. The active/important scripts are:

```text
generate_mock_reports.py       # mock Excel/data generation
upload_mock_reports.py         # loads generated files into DB
rebuild_energy_schedules.py    # DB-native energy schedule rebuild
init_database.py               # database initialization helper
```

Recommended target structure:

```text
scripts/
  db/
    init_database.py
    inspect_database.py
    clean_database.py
    check_railway_database.py
  data_generation/
    generate_mock_reports.py
    generate_7day_mock_data.py
    generate_15day_realistic_data.py
  ingestion/
    upload_mock_reports.py
    upload_to_railway.py
    upload_to_railway_fast.py
  energy_schedule/
    rebuild_energy_schedules.py
    calculate_energy_schedules.py
  diagnostics/
    verify_railway_deployment.py
    check_railway_status.py
```

Scripts with zero references in source/docs can likely move to archive first:

```text
add_client_columns.py
analyze_database.py
analyze_sch_structure.py
calculate_energy_schedules.py
calculate_mock_energy_schedules.py
check_energy_data.py
check_energy_schedule_data.py
check_report_types.py
check_summary_structure.py
create_excel_template.py
create_master_template.py
direct_insert_7day_mock.py
find_available_dates.py
generate_mock_transactions.py
generate_real_format_mocks.py
generate_sch_files.py
inspect_database.py
simple_calculation.py
simple_init_db.py
upload_7day_to_railway.py
upload_dor_only.py
upload_real_format_to_railway.py
upload_sch_to_railway.py
upload_to_railway.py
verify_railway_deployment.py
verify_story_3.py
```

Do not delete immediately; move to `archive/scripts/` unless we prove they are obsolete.

## Docs audit

Root has 29 Markdown files. This is too much for a clean SaaS repo.

Recommended target:

```text
README.md                      # single landing page
docs/
  architecture/
  operations/
  product/
  archived/
planning/
```

Likely current docs to consolidate:

```text
DASHBOARD_GUIDE.md
DATABASE_GUIDE.md
DEPLOYMENT_GUIDE.md
DEPLOY_TO_RAILWAY.md
RAILWAY_FIX_GUIDE.md
RAILWAY_STATUS.md
SETUP_INSTRUCTIONS.md
QUICK_START.md
README_DASHBOARD.md
README_NEW.md
README_FOR_COFOUNDER.md
PROJECT_SUMMARY.md
PROJECT_COMPLETE.md
```

Recommended action:

- Keep `README.md` concise.
- Move operational docs into `docs/operations/`.
- Move historical status/completion notes into `docs/archived/`.

## Runtime/generated artifacts

These should not be tracked long-term:

```text
power_trading.db
backend.pid
frontend.pid
backend.log
PowerTradingDashboard_*.zip
Data/*.xls
Data/*.xlsx
output/*.json
__pycache__/
.pytest_cache/
```

`.dockerignore` already excludes most of these from deployment. `.gitignore` should also be updated to ignore:

```text
*.db
*.pid
*.zip
```

Because `power_trading.db`, `backend.pid`, `frontend.pid`, and ZIP files are already tracked, we need a separate `git rm --cached` step to remove them from Git while keeping local copies.

## Recommended cleanup phases

### Phase 1 — Safety and hygiene

1. Add missing ignore rules for `*.db`, `*.pid`, `*.zip`.
2. Untrack local runtime artifacts:
   - `power_trading.db`
   - `backend.pid`
   - `frontend.pid`
   - `PowerTradingDashboard_*.zip`
3. Verify build and production API.
4. Commit as `chore: ignore runtime artifacts`.

### Phase 2 — Move root scripts

1. Create `scripts/` folders.
2. Move active scripts first.
3. Update references in `api/main.py`, docs, and shell/batch files.
4. Run smoke tests.

### Phase 3 — Archive legacy folders

1. Move `frontend/`, `desktop-wpf/`, and `power_trading_package/` into `archive/legacy/`.
2. Confirm Docker build still uses only `frontend-react/`.
3. Commit as `chore: archive legacy app copies`.

### Phase 4 — Documentation consolidation

1. Keep one root `README.md`.
2. Move setup/deployment docs under `docs/operations/`.
3. Move old completion/status docs under `docs/archived/`.

## Maintenance rules going forward

- Root should contain only project entry points and deployment config.
- Runtime state never goes into Git.
- Generated data lives in ignored folders or object storage, not source control.
- Scripts must live under `scripts/` with a clear purpose.
- Every script should be either:
  - used by app/deployment,
  - documented as an operator command,
  - or archived/deleted.
- One source of truth per feature. No duplicate app folders.
- Make small cleanup commits, one category at a time.
