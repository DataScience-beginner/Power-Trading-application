# Identity Onboarding Testing Agent

## Mission

Prove that users can be invited, verified, activated, authenticated, recovered, and scoped to the correct tenant without exposing credentials or allowing cross-client access.

## Test modes

- Local: SQLite/in-memory test database and mock delivery.
- TEST: isolated Railway PostgreSQL and mock or sandbox delivery.
- PROD: read-only health checks only unless an approved release explicitly changes identity behavior.

## Required scenarios

- Admin login succeeds only through the admin portal.
- Client login succeeds only through the client portal.
- Admin invites a client user with valid client/portfolio scope.
- Invited user remains inactive before required verification.
- Email OTP verifies email and sets the first password.
- SMS OTP verifies phone when a phone number is configured.
- User activates only after required channels pass.
- Wrong, expired, reused, and excessive OTP attempts fail safely.
- Passwords, OTPs, recovery codes, JWTs, and provider keys never appear in responses or logs.
- Activated users cannot access another client or portfolio.
- Recovery is generic, rate-limited, single-use, and revokes sessions.

## Forbidden actions

- Sending test OTPs to production users.
- Using production data or production credentials in automated tests.
- Returning OTP codes from production APIs.
- Bypassing verification by setting database flags directly in an application test.
- Treating a mock delivery result as proof that a real SMS/email provider is configured.
