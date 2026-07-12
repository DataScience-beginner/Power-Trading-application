---
name: release-management
description: Produce traceable release evidence and coordinate tested, approved, reversible promotion from DEV through TEST to PROD.
---

# Release Management Skill

Use this skill for releases, approvals, promotion, release notes, deployment evidence, incidents, or rollback.

1. Read `AGENT.md`, `checklist.md`, and `../../compliance/release_evidence_template.md`.
2. Record PR, commit SHA, migration revision, test results, deployment, backup, approval, and rollback target.
3. Reject any mismatch between tested and deployed commit.
4. Reject failed or silently skipped required gates.
5. Require independent production approval.
6. Record post-deployment health and known risks.
7. Create an incident record for emergency bypasses or failed production releases.
