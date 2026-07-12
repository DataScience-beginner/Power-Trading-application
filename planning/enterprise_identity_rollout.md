# Enterprise Identity Rollout

## Implemented Identity V1

- Separate admin and client login portals with server-enforced role matching.
- Database-backed revocable JWT sessions.
- Email and mobile OTP recovery adapters with generic responses.
- Hashed, single-use, ten-minute recovery challenges with attempt and request throttles.
- Password recovery revokes sessions and records security events.
- Break-glass administrator recovery retained as an internal service-key operation.

## Activation requirements

- Configure SMTP sender/domain credentials for email delivery.
- Configure an approved SMS webhook and verify E.164 phone ownership before SMS recovery.
- Add operational alerting for privileged recovery and repeated throttling.

## Next security milestone

- Mandatory passkey/WebAuthn or TOTP MFA for platform administrators.
- OIDC/SAML federation for enterprise clients.
- Rotating refresh-token cookies with CSRF controls.
- Risk-based login signals and recovery notifications through an independent channel.
