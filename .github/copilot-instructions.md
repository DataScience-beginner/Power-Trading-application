# Power Trading Application - AI Coding Guidelines

## Architecture Overview

This is a **hybrid Python backend + multi-frontend** power trading analytics platform that parses IEX trading Excel reports (DOR/SCH formats) into a universal JSON schema, stores them in PostgreSQL, and provides REST APIs for consumption.

### Core Data Flow
```
Excel Files (.xls/.xlsx) → Template Parsers → Universal JSON Schema → Database (PostgreSQL) → FastAPI → Frontend (React/WPF/HTML)
```

### Critical Components
- **Parsers** (`parsers/`): Template-based Excel parsers for DOR (Daily Obligation Reports) and SCH (Scheduling Reports)
- **Universal Schema** (`schemas/universal_trading_schema_v1.json`): Canonical data structure all parsers must output
- **Database Layer** (`database/`): SQLAlchemy ORM with service pattern - models define tables, services contain business logic
- **API Layer** (`api/main.py`): Single FastAPI file with 18+ endpoints (no routers yet, everything in main.py)
- **Frontend**: Three implementations - HTML/JS dashboard, React (TypeScript + MUI), WPF (.NET desktop - future)

## Key Technical Patterns

### 1. Parser Architecture Pattern
All parsers inherit from template-based design:
- **Auto .xls→.xlsx conversion**: Uses LibreOffice `soffice` command (see `_convert_xls_to_xlsx()`)
- **Format detection**: Parsers auto-detect GDAM vs Daily Obligation format
- **96 timeslots**: Every day = 96 × 15-minute intervals (00:00-23:45)
- **Zero-quantity handling**: Keep ALL transactions including zeros - they're meaningful for scheduling

Example from [parsers/DOR_Parser.py](parsers/DOR_Parser.py#L48):
```python
# CRITICAL: Don't filter out zero-quantity transactions in Daily Obligation format
buy_transactions = transactions  # Keep ALL, including zeros
```

### 2. Database Service Pattern
**Never write SQL in API routes** - use service layer functions:
- [database/services.py](database/services.py): CRUD operations for Client/Portfolio/DailyFile/Transaction
- [database/energy_schedule_service.py](database/energy_schedule_service.py): Calculation workflow logic
- **Upsert behavior**: `save_daily_file()` replaces existing files (max 6 files per portfolio per day)

### 3. File Upload & Parsing Workflow
1. Upload via `/api/upload` endpoint
2. Detect report type from filename pattern (GDAM/DAM/RTM for DOR, SCH pattern for SCH)
3. Parse with appropriate parser (DOR_Parser or SCH_Parser)
4. Extract `entity_id`, `portfolio_code` from metadata
5. Get-or-create Client → Portfolio → DailyFile (using service layer)
6. Save transactions (replace if duplicate)
7. Return parsed JSON + summary stats

### 4. Energy Schedule Calculation
**Two-day dependency**: Calculations require DOR (previous day) + SCH (current day)

Workflow in [database/energy_schedule_service.py](database/energy_schedule_service.py#L425):
```python
# For calculation_date (e.g., Jan 15):
dor_date = calculation_date - timedelta(days=1)  # Jan 14
sch_date = calculation_date  # Jan 15
# Need both dates' files to calculate
```

## Critical Commands & Workflows

### Local Development
```bash
# Install dependencies (dev container has apt access)
pip install -r requirements.txt --break-system-packages

# Initialize database (creates tables, runs migrations)
python scripts/db/init_database.py

# Start FastAPI server (port 8000)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Workflows
```bash
# Generate mock DOR/SCH reports
python scripts/data_generation/generate_mock_reports.py

# Upload all mock reports to database
python scripts/ingestion/upload_mock_reports.py

# Test calculation workflow
python -m pytest tests/test_calculation_workflow.py
```

## Data Model Hierarchy

```
Client (entity_id, entity_name)
  └─> Portfolio (portfolio_code, e.g., "NPT0019_TN0")
        └─> DailyFile (trading_date, report_type: "DOR_GDAM", "DOR_DAM", "DOR_RTM", "SCH_GDAM")
              └─> Transaction (96 timeslots per file, start_time, quantity, price)
```

**Key relationships**:
- One Client → Many Portfolios
- One Portfolio → Max 6 DailyFiles per day (3 DOR types + 3 SCH types)
- One DailyFile → 96 Transactions (15-min intervals)

See [database/models.py](database/models.py#L1-L100) for full schema.

## API Endpoint Patterns

All routes in [api/main.py](api/main.py) follow these conventions:
- **POST /api/upload**: File upload with multipart form data
- **GET /api/files**: List all parsed files with pagination
- **GET /api/data/{filename}**: Retrieve full parsed JSON
- **GET /api/analytics/summary**: Aggregate stats across all files
- **POST /api/calculate/energy-schedule**: Trigger calculation workflow
- **GET /api/energy-schedule/status**: Check calculation results

CORS is wide-open (`allow_origins=["*"]`) - restrict for production.

## Excel-Specific Gotchas

1. **LibreOffice dependency**: System must have `soffice` for .xls conversion (installed in dev container)
2. **Pandas engine**: Always use `engine='openpyxl'` for .xlsx files
3. **Header=None**: Trading reports have custom layouts - parse raw with `header=None`, then navigate by row index
4. **Regex patterns**: Time slots use patterns like `r'(\d{2}):(\d{2})\s*-\s*(\d{2}):(\d{2})'` - see parsers for examples

## Frontend Integration

- **HTML Dashboard** ([frontend/dashboard.html](frontend/dashboard.html)): Simple analytics UI, served at `/`
- **React App** ([frontend-react/](frontend-react/)): TypeScript + Material-UI + Redux Toolkit + Recharts
  - Run: `cd frontend-react && npm run dev` (Vite dev server)
  - Build: `npm run build` (outputs to `dist/`)
- **API expects**: Axios calls to `http://localhost:8000/api/*` endpoints

## When Adding Features

1. **New parser template**: Extend base pattern in `parsers/`, ensure output matches [schemas/universal_trading_schema_v1.json](schemas/universal_trading_schema_v1.json)
2. **New database model**: Add to [database/models.py](database/models.py), create migration, add service functions to [database/services.py](database/services.py)
3. **New API endpoint**: Add to [api/main.py](api/main.py), use `Depends(get_db)` for DB session
4. **New calculation**: Extend [database/energy_schedule_service.py](database/energy_schedule_service.py) - follow validate → calculate → store pattern

## Documentation References

- **Quick Start**: [QUICK_START.md](QUICK_START.md) - 5-minute test run
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Overall architecture decisions
- **Dashboard Guide**: [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) - Frontend usage
- **Energy Schedule**: [ENERGY_SCHEDULE_COMPLETE.md](ENERGY_SCHEDULE_COMPLETE.md) - Calculation workflow details
