# Innowatt Security Hardening Roadmap

This roadmap follows OWASP ASVS, OWASP automated-threat guidance, NIST CSF, and GitHub secure-use guidance. It is an engineering control plan, not a certification claim.

## Current status (2026-07-12)

| Phase | Status | Evidence / gap |
|---|---|---|
| Phase 1 — secure application | Code complete; activation pending | TOTP MFA, recovery codes, secure cookies, rate limits, headers, quarantine, scanner adapter and pinned actions are implemented. Production MFA encryption and mandatory antivirus must be activated after migration/scanner installation. |
| Phase 2 — public traffic | Integration complete; provider pending | Edge verification, bot-sensitive route enforcement, daily quotas, request IDs, structured alerts and webhook integration are implemented. A WAF/CDN and monitoring destination must inject/configure the production values. |
| Phase 3 — enterprise identity | Contract complete; provider pending | OIDC/SAML/SCIM/passkey/device-policy configuration contracts, posture reporting, tenant authorization and audit exports exist. Real federation and passkeys require customer IdP metadata and a selected WebAuthn implementation/provider. |
| Phase 4 — compliance readiness | Framework complete; independent evidence pending | Control matrix, evidence generator, DR exercise, penetration-test scope and vendor-risk template exist. Independent penetration testing, restore exercises and SOC 2/ISO assurance remain organizational activities. |

No phase is certified or production-complete solely because its design is documented.

## Phase 1 — secure application

- Configurable API rate limiting with stricter identity/upload limits.
- Security response headers and API no-store behavior.
- Workbook size, extension, signature, archive-path and macro validation.
- Quarantine filenames independent of user filenames.
- Optional ClamAV scanning with fail-closed `CLAMAV_SCAN_REQUIRED` mode.
- Dependency audit and CodeQL workflows.
- Immutable GitHub Action references.
- Dependabot for Python, npm and GitHub Actions.
- Configurable inactivity logout and JWT/session expiry.
- Encrypted RFC 6238 TOTP enrollment, one-time recovery codes, and administrator MFA policy.
- HttpOnly, Secure, SameSite browser-session cookies with bearer compatibility during migration.

## Phase 2 — public traffic protection

- Add Redis-backed rate limits before multi-replica deployment.
- Add WAF/CDN bot challenge for login, recovery, onboarding and upload routes.
- Structured security alerts with an optional webhook destination.
- Add API daily quotas and request correlation IDs.

Provider-dependent controls in Phase 2 require a selected WAF/CDN, Redis service, and verified identity provider. They must be configured in DEV/TEST before production.

## Phase 3 — enterprise identity and platform protection

- Enable mandatory ClamAV or managed malware scanning in TEST and PROD.
- Store uploads in private object storage rather than application disk.
- Encrypt sensitive data and restrict database/network access.
- Add external encrypted PostgreSQL backups and restore drills.
- Add container image scanning and SBOM publication.
- CI publishes Python and frontend CycloneDX SBOM evidence; container image scanning remains open.
- Add centralized logs, alerting and security-event retention.
- Environment-scoped OIDC/SAML/SCIM integration contracts and non-secret posture reporting.
- Device/session policy reporting and administrator-only audit export.
- Passkey activation remains provider/library dependent and disabled by default.

## Phase 4 — compliance readiness

- SAML/OIDC SSO with a customer identity provider.
- SCIM user and group provisioning.
- Role/tenant mapping from signed identity claims plus server-side authorization.
- Security review, penetration test, vendor risk review and incident exercises.
- SOC 2/ISO 27001 evidence mapping if commercially required.
- Machine-readable repository control evidence, DR exercise procedure, penetration-test scope, and vendor-risk template.

## Release gates

No phase is production-complete until:

1. The control is implemented in DEV.
2. Automated tests cover success and abuse cases.
3. TEST validates the control with synthetic data.
4. Evidence and rollback instructions exist.
5. Production provider credentials are configured separately.
6. The cofounder approves the production release.
