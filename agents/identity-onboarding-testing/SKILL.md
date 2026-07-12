---
name: identity-onboarding-testing
description: Test admin/client login, invited-client onboarding, email verification, SMS OTP, password activation, recovery, rate limits, and tenant-safe authentication.
---

# Identity Onboarding Testing Skill

Use this skill before commits or deployments that affect authentication, signup, invitations, email, SMS, OTP, recovery, sessions, roles, or tenant access.

1. Read `AGENT.md`, `checklist.md`, and `../../compliance/cofounder_onboarding.md`.
2. Use a local or TEST database only; never send test codes through production providers.
3. Set `IDENTITY_DELIVERY_MODE=mock` for deterministic local/TEST tests.
4. Validate admin and client portal role separation.
5. Validate invite → email verification → SMS verification → password setup → activation.
6. Validate wrong, expired, reused, and rate-limited codes.
7. Validate tenant and portfolio boundaries after activation.
8. Run `python scripts/quality/golden_test.py --mode rigorous` and report every failed or skipped check.
