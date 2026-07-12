# Identity and Onboarding Execution Plan

## Implemented flow

```text
Admin login
   ↓
Admin invites client with client/portfolio scope
   ↓
Inactive client identity created
   ↓
Email verification challenge sent
   ↓ optional/required when phone exists ↓
SMS verification challenge sent
   ↓
Client sets first password
   ↓
Required channels verified
   ↓
Client becomes active
   ↓
Client portal login with tenant scope
```

## Delivery modes

| Environment | `IDENTITY_DELIVERY_MODE` | Behavior |
|---|---|---|
| Local | `mock` | Captures messages in memory; no external send |
| TEST | `mock` or approved sandbox | Safe validation with synthetic identities |
| PROD | `provider` | SMTP and SMS webhook/provider credentials required |

Mock delivery is never proof that a real provider is configured. Real provider enablement requires security review, verified sender/domain, rate limits, and a delivery test.

## API contracts

- `POST /api/v1/identity/onboarding/invite` — admin-only client invitation.
- `POST /api/v1/identity/onboarding/verify` — single-use email/SMS verification and initial password setup.
- `GET /api/v1/identity/onboarding/{user_id}` — admin-only non-secret status.
- `POST /api/v1/identity/login` — role-aware login after activation.
- Existing recovery endpoints remain separate and continue to revoke sessions.

## Test requirements

- Valid admin/client portal separation.
- Client and portfolio scope validation.
- Email and SMS code verification.
- Activation only after required channels pass.
- Wrong, expired, reused, and rate-limited codes.
- Password and session behavior.
- Tenant isolation after activation.
- No OTP, password, token, or provider-key leakage.

Use the [Identity Onboarding Testing Skill](../agents/identity-onboarding-testing/SKILL.md) and run the rigorous golden gate before promotion.
