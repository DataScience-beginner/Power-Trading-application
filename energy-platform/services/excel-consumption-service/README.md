# Excel Consumption Service

Backend service responsible for:

- workbook upload intake
- source sheet parsing
- tenant-scoped storage
- deterministic `Solar Working` calculation
- API delivery to the client web portal

This service starts on SQLite for local development and should migrate to
PostgreSQL later through SQLAlchemy and Alembic migrations.

## Migration Workflow

Run migrations before starting the API:

```bash
alembic upgrade head
```

Create a new revision when the ORM models change:

```bash
alembic revision -m "describe-change"
```
