# Identity Onboarding Testing Checklist

- [ ] Test database is isolated.
- [ ] Mock delivery is explicit.
- [ ] Admin role and portal tested.
- [ ] Client role and portal tested.
- [ ] Valid invitation tested.
- [ ] Invalid client/portfolio scope rejected.
- [ ] Email OTP tested.
- [ ] SMS OTP tested with `+91` E.164 format.
- [ ] Wrong, expired, reused, and rate-limited codes tested.
- [ ] User activation state tested.
- [ ] Password login tested after activation.
- [ ] Tenant isolation tested.
- [ ] Recovery/session revocation tested.
- [ ] No secret or OTP leakage detected.
- [ ] Rigorous golden gate passed.
