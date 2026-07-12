# Innowatt Security Hardening Roadmap

This roadmap follows OWASP ASVS, OWASP automated-threat guidance, NIST CSF, and GitHub secure-use guidance. It is an engineering control plan, not a certification claim.

## Phase 1 — application baseline (implemented in this increment)

- Configurable API rate limiting with stricter identity/upload limits.
- Security response headers and API no-store behavior.
- Workbook size, extension, signature, archive-path and macro validation.
- Quarantine filenames independent of user filenames.
- Optional ClamAV scanning with fail-closed `CLAMAV_SCAN_REQUIRED` mode.
- Dependency audit and CodeQL workflows.
- Immutable GitHub Action references.
- Dependabot for Python, npm and GitHub Actions.
- Configurable inactivity logout and JWT/session expiry.

## Phase 2 — identity and anti-automation hardening

- Replace browser-readable bearer-token storage with HttpOnly Secure SameSite cookie sessions.
- Add admin TOTP/passkey MFA and recovery-code lifecycle.
- Add Redis-backed rate limits before multi-replica deployment.
- Add WAF/CDN bot challenge for login, recovery, onboarding and upload routes.
- Add suspicious-login alerts and device/session management.
- Add API tenant quotas and request correlation IDs.

Provider-dependent controls in Phase 2 require a selected WAF/CDN, Redis service, and verified identity provider. They must be configured in DEV/TEST before production.

## Phase 3 — data and platform protection

- Enable mandatory ClamAV or managed malware scanning in TEST and PROD.
- Store uploads in private object storage rather than application disk.
- Encrypt sensitive data and restrict database/network access.
- Add external encrypted PostgreSQL backups and restore drills.
- Add container image scanning and SBOM publication.
- Add centralized logs, alerting and security-event retention.

## Phase 4 — enterprise identity and governance

- SAML/OIDC SSO with a customer identity provider.
- SCIM user and group provisioning.
- Role/tenant mapping from signed identity claims plus server-side authorization.
- Security review, penetration test, vendor risk review and incident exercises.
- SOC 2/ISO 27001 evidence mapping if commercially required.

## Release gates

No phase is production-complete until:

1. The control is implemented in DEV.
2. Automated tests cover success and abuse cases.
3. TEST validates the control with synthetic data.
4. Evidence and rollback instructions exist.
5. Production provider credentials are configured separately.
6. The cofounder approves the production release.
