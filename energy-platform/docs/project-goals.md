# Project Goals

## Business Goal

Build a client-facing web application that accepts uploaded Excel workbooks in
the known power-consumption format and automatically produces the `Solar Working`
result without depending on workbook formulas.

## First Service Goal

The first service is `excel-consumption-service`.

Its responsibility is to:

- accept workbook uploads
- parse `DAM`, `RTM`, `TNEB`, and future `Solar` input sheets
- normalize source data into a unified database model
- generate daily `Solar Working` rows in backend code
- expose results through APIs for the web portal

## Platform Goal

This should evolve into a multi-service energy platform rather than remain a
single-purpose Excel utility.

The platform must support:

- many services in the future
- many clients with separate data isolation
- common data models across clients
- client-level customization without schema fragmentation
- both vendor-hosted and client-hosted deployment models
- later AI recommendation and insight services

## Non-Goals For The First Iteration

- no desktop-specific code yet
- no AI-driven calculation logic
- no client-specific schema forks
- no hard dependency on PostgreSQL before development starts

## Architecture Constraints

- backend logic must be deterministic and auditable
- tenant scoping must be explicit in models and APIs
- service metadata must be trackable for future service scale
- SQLite should work now; PostgreSQL should be a config migration later
- frontend should consume APIs, not workbook files directly
