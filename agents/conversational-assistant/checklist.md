# Conversational Assistant Checklist

- JWT secret is configured and at least 32 characters.
- User is active and role/client membership comes from the database.
- Portfolio restrictions are enforced.
- Conversation ownership is enforced.
- Date range is bounded to at most 366 days.
- Prompt injection and consequential-action language are rejected first.
- Only approved deterministic tools are invoked.
- Model input contains minimum scoped structured facts.
- Verified facts are appended independently of model output.
- Provider fallback, timeout, and rate-limit behavior are tested.
- Evidence, confidence, limitations, model, prompt, token, and safety metadata are stored.
