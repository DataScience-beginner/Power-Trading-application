# Identity Security Checklist

- Portal role is enforced from database state.
- Password and token material is never logged or returned.
- Recovery response does not enumerate accounts.
- Challenge is cryptographically random, hashed, single-use, attempt-limited, and expired after ten minutes.
- Requests are throttled by hashed identifier.
- Email or mobile destination is verified before delivery.
- Password recovery revokes active sessions.
- Success, denial, throttling, and privileged recovery are audited.
- Tenant and portfolio authorization remains independent of frontend state.
