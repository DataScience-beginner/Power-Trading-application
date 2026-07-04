# Data Model Outline

## Core Entities

### Tenant

Represents a client boundary.

Fields to keep from the start:

- tenant code
- tenant name
- active status
- deployment mode

### Site

Represents a plant or operating location under a tenant.

Fields to keep from the start:

- site code
- site name
- timezone
- tenant foreign key

### User

Represents a human account that can log in to the system.

### Role

Represents a reusable permission group.

Initial roles:

- `platform_admin`
- `tenant_admin`
- `client_viewer`

### User Role Assignment

Maps users to roles, optionally scoped to a tenant.

### Workbook Upload

Represents one uploaded Excel file and its metadata.

### Sheet Ingestion

Tracks each source sheet parsed from a workbook, its status, and validation.

### Source Interval Record

Represents time-block market data from `DAM`, `RTM`, and future interval-based
sources.

### Daily Consumption Record

Represents daily values from `TNEB` and future daily sources.

### Solar Daily Record

Represents future direct solar inputs once that sheet is standardized.

### Solar Working Result

Represents the calculated per-day output:

- date
- category totals
- IEX totals
- solar totals
- net balance
- banking balance

### Calculation Run

Tracks one execution of the calculation engine for audit and repeatability.

## Modeling Principles

- every business table must be tenant-scoped
- workbook source data and calculated result must both be stored
- raw import traceability must be retained
- result tables should be reproducible from source data
- schema should avoid SQLite-specific assumptions
- auth and RBAC must be database-backed, not hardcoded in frontend logic
