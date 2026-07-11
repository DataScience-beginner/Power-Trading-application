# Conversational Assistant Agent

## Mission

Answer authenticated energy questions using only authorized, typed, tenant-scoped tools and verified evidence.

## Workflow

1. Resolve user identity and role from signed JWT and current database state.
2. Authorize the conversation's fixed client/portfolio scope.
3. Reject prompt injection, credentials, arbitrary SQL, forecasting, mutation, bidding, and trading requests.
4. Route supported questions to deterministic quality or market tools.
5. Optionally ask the configured model to narrate already-verified facts.
6. Append authoritative facts independently of model prose.
7. Store messages, tools, evidence, confidence, limitations, provider/model, tokens, and safety status.

## Model boundary

Groq `llama-3.1-8b-instant` is the initial optional free-tier narrator. It receives no credentials, database connection, or executable tools. If it fails or has no key, use deterministic narration. The model never becomes the source of numerical truth.
