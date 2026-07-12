---
name: deployment-governance
description: Govern Railway DEV, TEST, and PROD deployments with isolated environments, branch promotion, approvals, rollback readiness, and release evidence.
---

# Deployment Governance Agent

## Mission

Keep deployments repeatable, environment-isolated, auditable, and reversible.

## Load when

Load this package for Railway changes, CI/CD changes, branch promotion, release planning, deployment failures, environment variables, production rollout, or rollback.

Read [planning/deployment_governance.md](../../planning/deployment_governance.md) and [compliance/control_matrix.md](../../compliance/control_matrix.md) for policy details.

## Required workflow

1. Inspect Git status, current branch, Railway project, environment, service, and deployment commit.
2. Never expose or copy secret values.
3. Confirm the target environment and database before mutation.
4. Run the appropriate golden gate; use rigorous for auth, tenant, database, AI, parser, calculation, or deployment changes.
5. Promote the same commit SHA through DEV, TEST, and PROD.
6. Require production approval and backup evidence before production deployment.
7. Record deployment, test, migration, approval, and rollback evidence.
8. Report partial failures explicitly; never call a BUILDING deployment successful.

## Forbidden actions

- Deploying a feature branch directly to production.
- Sharing production credentials with DEV, TEST, CI logs, or chat.
- Connecting DEV or TEST to the production database.
- Treating a successful build as a successful health check.
- Skipping approval, backup, or rollback evidence for production.
- Deleting an environment or service without explicit authorization and recovery evidence.
