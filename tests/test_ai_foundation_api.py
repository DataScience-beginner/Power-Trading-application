"""HTTP-level AI Foundation contract tests using an isolated in-memory database."""

import asyncio

from fastapi import FastAPI
import httpx

from api.routers.ai_foundation import router


def request(app: FastAPI, method: str, path: str, **kwargs) -> httpx.Response:
    """Call the ASGI app without starting the production lifespan."""
    async def execute() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(execute())


def test_capability_catalog_is_public_and_explicit() -> None:
    app = FastAPI()
    app.include_router(router)
    response = request(app, "GET", "/api/v1/ai-foundation/capabilities")
    assert response.status_code == 200
    payload = response.json()
    assert payload["canonical_schema_status"].startswith("evolving")
    assert "synthetic-v0" in payload["mock_data_status"]
    assert any(item["capability_id"] == "decision.record" for item in payload["capabilities"])

    schema = app.openapi()
    protected_operation = schema["paths"]["/api/v1/ai-foundation/entities"]["post"]
    header_names = {item["name"] for item in protected_operation["parameters"] if item["in"] == "header"}
    assert "x-ai-foundation-key" in header_names
