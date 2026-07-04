# Railway Deployment

Deploy this repository to Railway as two separate services:

- `excel-consumption-service` for the FastAPI backend
- `client-web` for the React frontend

## Why two services

The frontend and backend have different runtime needs. Keeping them separate in
Railway maps directly to the existing service-oriented structure and keeps the
deployment model clean.

## Backend service

Root directory:

```text
services/excel-consumption-service
```

Recommended environment variables:

```text
EXCEL_CONSUMPTION_UPLOAD_DIR=/app/data/uploads
EXCEL_CONSUMPTION_DEFAULT_TENANT=demo-tenant
EXCEL_CONSUMPTION_JWT_SECRET=replace-this-with-a-real-secret
```

For PostgreSQL on Railway, set:

```text
EXCEL_CONSUMPTION_DATABASE_URL=${{Postgres.DATABASE_URL}}
```

After the frontend service has a public domain, also set:

```text
EXCEL_CONSUMPTION_ALLOWED_ORIGINS=["https://<frontend-domain>"]
```

Backend healthcheck path:

```text
/health
```

### SQLite fallback

If you temporarily remain on SQLite instead of PostgreSQL, attach a Railway
Volume and mount it at:

```text
/app/data
```

That will persist:

- the SQLite database
- uploaded workbook files

For production, PostgreSQL is the recommended path.

## Frontend service

Root directory:

```text
apps/client-web
```

Required environment variable:

```text
VITE_API_BASE_URL=https://<backend-domain>
```

The frontend Docker build consumes this as a build argument and compiles the
correct API base URL into the app.

## Railway UI deployment steps

1. Push the repository to GitHub.
2. Create a new Railway project.
3. Add a service from GitHub for the backend.
4. Set the backend root directory to `services/excel-consumption-service`.
5. Add PostgreSQL to the Railway project.
6. Add the backend variables listed above.
7. Set `EXCEL_CONSUMPTION_DATABASE_URL` to `${{Postgres.DATABASE_URL}}`.
8. If staying on SQLite instead, attach a volume mounted at `/app/data`.
9. Set the backend healthcheck path to `/health`.
10. Deploy the backend.
11. Copy the backend public domain.
12. Add a second service from the same GitHub repository for the frontend.
13. Set the frontend root directory to `apps/client-web`.
14. Set `VITE_API_BASE_URL` to the backend public domain.
15. Deploy the frontend.
16. Copy the frontend public domain.
17. Go back to the backend service and set `EXCEL_CONSUMPTION_ALLOWED_ORIGINS` to the frontend domain.
18. Redeploy the backend.

## Important runtime note

Railway injects a `PORT` environment variable at runtime. Both Dockerfiles are
configured to bind to that value automatically.

## Recommended production direction

- Use Railway PostgreSQL instead of SQLite for production.
- Keep the backend and frontend as separate services.
- Add a custom domain after the first successful deploy.
