# Innowatt Control Matrix

This is the lightweight control register for the DEV → TEST → PROD delivery process. It maps practical controls to NIST SSDF, AWS Well-Architected themes, and software supply-chain expectations. It is not a certification statement.

| Control | Implementation | Evidence | Owner | Gate |
|---|---|---|---|---|
| Change review | Pull request required for protected branches | PR, review, status checks | Release Agent | Merge |
| Quality validation | Golden standard/rigorous test runner | Workflow artifact and summary | Testing QA Agent | Deploy |
| Secret protection | `.gitignore`, secret scan, environment secrets | Scan result, secret inventory | Security Compliance Agent | Merge |
| Dependency hygiene | Python and npm audit reports | Workflow artifact | Security Compliance Agent | Merge |
| Tenant isolation | Client/portfolio authorization tests | Test report | Identity Security Agent | DEV/TEST |
| Environment isolation | Separate Railway app and PostgreSQL services | Railway environment inventory | Deployment Agent | Deploy |
| Data protection | DEV synthetic, TEST controlled, PROD real | Dataset classification | Data Quality Agent | Deploy |
| Migration safety | Additive migration and staged validation | Migration report | Database specialist | TEST/PROD |
| Approval separation | Cofounder required for production environment | GitHub deployment approval | Cofounder | PROD |
| Release traceability | Commit, migration, test and deployment metadata | Release evidence | Release Agent | PROD |
| Recovery | External encrypted PostgreSQL dump and restore runbook | Backup checksum/location | Operations owner | PROD |
| Availability | Health checks, restart policy, post-deploy smoke | Railway and workflow logs | Deployment Agent | Deploy |
| AI governance | Tool allowlist, evidence, confidence, tenant scope | AI test/audit record | AI Governance Agent | AI changes |
| API abuse resistance | Scoped rate limits, security headers and API no-store responses | Security control tests and deployment variables | Security Compliance Agent | DEV/TEST |
| Upload safety | Type/signature/archive validation, quarantine names, macro policy and optional AV scan | Upload security tests and scanner evidence | Security Compliance Agent | DEV/TEST |
| Supply-chain integrity | Pinned workflow actions, dependency audits, CodeQL and Dependabot | Workflow results and dependency updates | Security Compliance Agent | Merge |

## Review cadence

- Every pull request: automated controls.
- Every release: release evidence.
- Monthly: access, secrets, dependencies, backup and DORA review.
- Quarterly: restore test, tenant-boundary review, incident exercise and control update.
