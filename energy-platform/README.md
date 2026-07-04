# Energy Platform

Service-oriented platform for client-facing energy data applications.

The first service in this platform is `excel-consumption-service`, which ingests
uploaded Excel workbooks and generates the `Solar Working` result from source
data such as `DAM`, `RTM`, `TNEB`, and future `Solar` sheets.

## Platform Goals

- Replace manual Excel-based calculation with backend services.
- Keep a unified data model across clients.
- Enforce tenant isolation so client data never leaks across tenants.
- Start with SQLite for development and migrate to PostgreSQL later.
- Keep the architecture web-first now, while allowing a desktop wrapper later.
- Make each capability trackable as an independent service.
- Add AI recommendations later without mixing AI into deterministic calculations.

## Workspace Layout

- `apps/client-web`: client-facing React web portal
- `services/excel-consumption-service`: backend service for ingestion and calculation
- `packages/service-registry`: service tracking metadata
- `packages/shared-config`: shared settings and future common libraries
- `docs`: project goals, architecture, and data model notes
- `infrastructure`: Docker, monitoring, and deployment scaffolding

## Immediate Scope

1. Upload workbook in the supported format.
2. Parse `DAM`, `RTM`, `TNEB`, and later `Solar`.
3. Store uploaded and calculated data in a tenant-aware database model.
4. Generate `Solar Working` rows in backend code.
5. Expose results through APIs and show them in the web portal.

## Next Build Direction

- Finalize unified data model
- Implement workbook ingestion pipeline
- Implement `Solar Working` calculation engine
- Build upload and result dashboard flows
- Add auth, tenant controls, audit, and observability

## Database Versioning

The backend service now uses Alembic for schema versioning.

Run this from `services/excel-consumption-service` before starting the API:

```bash
alembic upgrade head
```

## One-Command Startup

To build and start the core web application stack from a fresh clone:

```bash
./start.sh
```

To stop it:

```bash
./stop.sh
```

To fully wipe containers, named volumes, locally built images, and runtime
database files so you can start again from a clean state:

```bash
./reset.sh --force
```

### Why These Matter

- `.env`-driven startup:
  lets you change ports, image names, container database paths, and allowed
  origins per machine or environment without editing tracked files.
- `start.sh`:
  gives one predictable entrypoint for a fresh clone, demo server, or client
  environment handoff.
- `stop.sh`:
  shuts services down without deleting state, which is the normal operator flow.
- `reset.sh`:
  is useful when you want to reproduce a clean install, remove broken test data,
  clear old images, or recover from migration experiments.
- CI workflow:
  protects the repo by checking backend imports, schema migration viability,
  frontend builds, compose rendering, and container builds before merges.

Available endpoints after startup:

- Web app: `http://localhost:4173`
- API: `http://localhost:8000`

Observability containers are scaffolded in Compose, but they are not started by
default from `./start.sh`.

## Railway Deployment

This repository is ready to deploy to Railway as two services:

- Backend: `services/excel-consumption-service`
- Frontend: `apps/client-web`

Detailed instructions are in:

```text
docs/railway-deployment.md
```

## Runtime Note

Docker Engine is the preferred runtime for this stack.

The startup script also supports rootless Podman. On hosts where the home
directory is NFS-backed or subordinate UID/GID mappings are unavailable, the
scripts automatically redirect Podman storage to `/tmp` and enable the
compatibility settings needed for this project to build and run.
