"""Deterministic application security control tests."""

from io import BytesIO
import zipfile

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from api.security.http_security import ApiSecurityMiddleware
from api.security.upload_security import validate_workbook
from api.services.security_governance_service import enterprise_identity_status, security_posture


def xlsx_bytes(*names: str) -> bytes:
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for name in names or ["[Content_Types].xml"]:
            archive.writestr(name, "test")
    return stream.getvalue()


def test_upload_security_accepts_normal_xlsx() -> None:
    assert validate_workbook("report.xlsx", xlsx_bytes()) == ".xlsx"


@pytest.mark.parametrize("filename,content", [
    ("report.txt", b"not a workbook"),
    ("report.xlsx", b"not a zip"),
    ("report.xls", b"not an ole file"),
])
def test_upload_security_rejects_invalid_workbook(filename: str, content: bytes) -> None:
    with pytest.raises(HTTPException):
        validate_workbook(filename, content)


def test_upload_security_rejects_macro_workbook(monkeypatch) -> None:
    monkeypatch.setenv("ALLOW_MACRO_FILES", "false")
    with pytest.raises(HTTPException) as error:
        validate_workbook("report.xlsx", xlsx_bytes("xl/vbaProject.bin"))
    assert error.value.status_code == 400


def test_upload_security_rejects_oversized_workbook(monkeypatch) -> None:
    monkeypatch.setenv("UPLOAD_MAX_BYTES", "10")
    with pytest.raises(HTTPException) as error:
        validate_workbook("report.xlsx", xlsx_bytes())
    assert error.value.status_code == 413


def test_security_posture_never_returns_secret_values(monkeypatch) -> None:
    monkeypatch.setenv("WAF_VERIFICATION_SECRET", "must-not-be-returned")
    monkeypatch.setenv("OIDC_CLIENT_SECRET", "must-not-be-returned")
    payload = security_posture().model_dump_json() + enterprise_identity_status().model_dump_json()
    assert "must-not-be-returned" not in payload


def test_enterprise_identity_status_is_fail_closed(monkeypatch) -> None:
    monkeypatch.delenv("OIDC_ISSUER_URL", raising=False)
    monkeypatch.delenv("SCIM_BEARER_TOKEN", raising=False)
    status = enterprise_identity_status()
    assert status.oidc_configured is False
    assert status.scim_configured is False


def security_client() -> TestClient:
    app = FastAPI()
    app.add_middleware(ApiSecurityMiddleware)

    @app.get("/api/check")
    async def check() -> dict[str, bool]:
        return {"ok": True}

    @app.post("/api/v1/identity/check")
    async def identity_check() -> dict[str, bool]:
        return {"ok": True}

    return TestClient(app)


def test_security_middleware_adds_headers_and_request_id(monkeypatch) -> None:
    monkeypatch.setenv("API_TENANT_DAILY_QUOTA", "100")
    response = security_client().get("/api/check")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-request-id"]
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_waf_verification_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("WAF_VERIFICATION_REQUIRED", "true")
    monkeypatch.setenv("WAF_VERIFICATION_SECRET", "edge-secret")
    client = security_client()
    assert client.post("/api/v1/identity/check").status_code == 403
    assert client.post("/api/v1/identity/check", headers={"X-WAF-Verified": "edge-secret"}).status_code == 200


def test_daily_api_quota_is_enforced(monkeypatch) -> None:
    monkeypatch.setenv("API_TENANT_DAILY_QUOTA", "1")
    client = security_client()
    assert client.get("/api/check").status_code == 200
    assert client.get("/api/check").status_code == 429
