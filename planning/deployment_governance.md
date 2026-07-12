# Innowatt Delivery and Compliance Framework

## Purpose

This framework makes every change traceable from pull request to Railway deployment. It is designed for a small, AI-assisted team while preserving enterprise controls: isolated environments, least privilege, automated evidence, two-person production approval, rollback readiness, and tenant-safety checks.

This is an internal control framework, not a claim of SOC 2, ISO 27001, or regulatory certification. Certification requires an independent assessment.

## Environment model

| Environment | Branch | Database | Data | Deployment authority |
|---|---|---|---|---|
| DEV | `develop` | DEV PostgreSQL | Synthetic only | Automatic after CI |
| TEST | `staging` | TEST PostgreSQL | Synthetic or anonymized | Automatic after DEV promotion |
| PROD | `V2` until a planned rename to `main` | Existing production PostgreSQL | Real tenant data | Protected approval |

No environment may reuse another environment's database URL, JWT secret, identity pepper, or recovery-provider credentials.

## Promotion policy

1. A specialist works on a feature branch and opens a pull request.
2. Pull-request checks run QC, compile, frontend build, tests, secret scanning, and dependency checks.
3. A merge to `develop` deploys DEV through Railway's branch integration.
4. DEV smoke and tenant-isolation checks pass before the same commit is promoted to `staging`.
5. TEST runs rigorous regression, API contract, migration, security, and controlled UAT checks.
6. A pull request from `staging` to `V2` is reviewed by the cofounder.
7. Production deployment requires the protected GitHub `production` environment approval and a backup/rollback confirmation.
8. The deployed commit SHA and migration revision are recorded in release evidence.

The production path never accepts an unreviewed direct push. Emergency changes require an incident record, explicit approval, and a follow-up review.

## Mandatory pipeline gates

### Code and repository

- No tracked secrets, credentials, runtime databases, logs, archives, or build output.
- Source files remain within the repository's 1,000-line target and 1,500-line hard ceiling.
- API changes update `api/endpoint_registry.yaml`.
- Database changes include a reviewed, additive migration and rollback notes.

### Security and supply chain

- Least-privilege GitHub Actions permissions.
- Environment-scoped secrets; production secrets are never available to DEV or TEST jobs.
- Secret and dependency scanning on pull requests.
- Pinned or reviewed third-party actions where practical.
- Build provenance and commit SHA recorded with each release.

### Application quality

- Golden standard checks for normal changes.
- Golden rigorous checks for auth, tenant, database, parser, calculation, chatbot, AI, and deployment changes.
- Frontend production build.
- API health and endpoint contract checks.
- Tenant-isolation tests for every client-facing endpoint.

### Data and operations

- Production PostgreSQL backup before schema or release changes.
- No mock-data loading or database reset in production.
- Health checks after deployment.
- Rollback target identified before approval.
- Incident and recovery evidence retained.

## Release evidence

Each production release must retain:

- pull request URL and approvals;
- commit SHA and branch;
- test workflow URL and results;
- database migration revision;
- deployment URL and timestamp;
- backup confirmation;
- smoke-test result;
- rollback target;
- known risks and follow-up owner.

Use [../compliance/release_evidence_template.md](../compliance/release_evidence_template.md).

## Rollback

Application rollback uses the last known-good Railway deployment or commit. Database rollback is not assumed to be automatic: prefer backward-compatible additive migrations, restore from the external PostgreSQL dump when necessary, and document the decision in the incident record.

## Metrics

Review monthly:

- deployment frequency;
- change lead time;
- change failure rate;
- failed deployment recovery time;
- deployment rework rate;
- escaped defects;
- tenant-isolation test failures;
- backup age and restore-test age.
