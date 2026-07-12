---
name: security-compliance
description: Apply secret hygiene, dependency controls, tenant protection, least privilege, auditability, and secure software delivery checks.
---

# Security Compliance Skill

Use this skill for security, compliance, secrets, dependencies, tenant isolation, supply-chain, audit, or production-hardening work.

1. Read `AGENT.md`, `checklist.md`, and `../../compliance/control_matrix.md`.
2. Scan tracked files and dependencies without printing secrets.
3. Keep runtime secrets in environment-scoped secret stores.
4. Verify production data and credentials cannot enter DEV/TEST workflows.
5. Require tenant-isolation tests for client-facing changes.
6. Record findings, owners, due dates, and explicit risk acceptance.
7. Do not weaken a gate to obtain a green build.
8. Run `python scripts/security/generate_control_evidence.py` for security releases.
9. Treat WAF, SSO/SCIM, passkeys, penetration tests, and certifications as incomplete until provider or independent evidence exists.
