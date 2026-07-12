"""Deterministic application security control tests."""

from io import BytesIO
import zipfile

import pytest
from fastapi import HTTPException

from api.security.upload_security import validate_workbook


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
