---
name: deployment-governance
description: Govern Railway DEV, TEST, and PROD deployments with isolated environments, branch promotion, approval gates, rollback readiness, and release evidence.
---

# Deployment Governance Skill

Use this skill for Railway, CI/CD, environment, release, promotion, rollback, or production deployment work.

1. Read `AGENT.md`, `checklist.md`, and `../../planning/deployment_governance.md`.
2. Verify target environment, branch, service, database, and commit SHA before mutation.
3. Never expose or copy secrets.
4. Run the risk-appropriate golden gate; use rigorous for auth, tenant, database, AI, parser, calculation, or deployment changes.
5. Promote the same commit through DEV → TEST → PROD.
6. Require production approval, backup evidence, health checks, and a rollback target.
7. Report BUILDING, FAILED, and SUCCESS states distinctly.
