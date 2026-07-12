# Identity Onboarding Testing Memory

- Local and TEST use `IDENTITY_DELIVERY_MODE=mock`.
- Production provider configuration is separate and never copied into tests.
- A phone-enabled invitation requires both email and SMS verification before activation.
- The reference test phone is `+919884455466`; do not send real messages during automated tests.
