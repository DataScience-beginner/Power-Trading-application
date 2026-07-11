# Testing QA Agent Memory

## Stable project testing context

- The repository already has several historical `tests/` files, but many are story/manual tests that print output or depend on local/Railway state.
- The first reliable gate should be a golden pipeline that is deterministic and fast.
- API integration tests must be timeout-bounded because direct FastAPI TestClient startup previously hung while touching application startup/database behavior.
- The production app uses Railway PostgreSQL through `DATABASE_URL`.
- Local SQLite files and generated Excel reports must not be treated as production truth.

## Current baseline

- Standard pre-commit gate should start with:
  - Git hygiene.
  - Python compile.
  - Golden static contracts.
  - Frontend build.
- Historical manual tests were moved to `archive/legacy/tests/manual/` because they relied on localhost, Railway network, generated `Data/`, or mutable local DB state.
- Rigorous gate currently runs the deterministic active suite; manual tests must be converted into isolated integration tests before returning to `tests/`.

## Follow-ups

- Convert old story tests into deterministic unit/integration tests.
- Add a controlled test database profile.
- Add API contract tests with explicit timeout and DB isolation.
- Add chatbot/tool endpoint tests once assistant APIs are introduced.
