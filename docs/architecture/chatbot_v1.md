# Authenticated Conversational Assistant V1

The chatbot does not contain all client data in its model. It retrieves the minimum authorized facts through deterministic tools, then optionally uses Groq `llama-3.1-8b-instant` to improve wording.

```text
JWT user -> database role/scope -> fixed conversation scope -> safety router
 -> approved deterministic tool -> verified evidence -> optional Groq narration
 -> independently appended facts -> persisted message/audit metadata
```

Required Railway variables:

- `JWT_SECRET_KEY` — independently generated, minimum 32 characters.
- `AI_FOUNDATION_API_KEY` — internal bootstrap/service operations.
- `GROQ_API_KEY` — optional free-tier model narration.
- `GROQ_MODEL=llama-3.1-8b-instant`.

The first administrator is created once through `/api/v1/auth/bootstrap-admin` using the AI Foundation service credential. Later users are created by an authenticated platform administrator.

The model never receives database credentials, arbitrary SQL, cross-client data, or executable market tools. Deterministic answers remain available when Groq is absent, rate-limited, or unavailable.
