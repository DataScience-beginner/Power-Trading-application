"""Workbook quarantine, type validation, and optional antivirus scanning."""

from __future__ import annotations

from io import BytesIO
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

from fastapi import HTTPException


ALLOWED_WORKBOOK_EXTENSIONS = {".xls", ".xlsx"}


def max_upload_bytes() -> int:
    """Return the configured maximum workbook size."""
    return int(os.getenv("UPLOAD_MAX_BYTES", str(25 * 1024 * 1024)))


def validate_workbook(filename: str | None, content: bytes) -> str:
    """Validate filename, size, workbook signature, archive paths, and macros."""
    if not filename:
        raise HTTPException(status_code=400, detail="File name is required.")
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_WORKBOOK_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .xls and .xlsx workbooks are supported.")
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    limit = max_upload_bytes()
    if len(content) > limit:
        raise HTTPException(status_code=413, detail=f"File exceeds the {limit // (1024 * 1024)} MB upload limit.")
    if extension == ".xls" and not content.startswith(b"\xd0\xcf\x11\xe0"):
        raise HTTPException(status_code=400, detail="The uploaded .xls file signature is invalid.")
    if extension == ".xlsx":
        if not content.startswith(b"PK"):
            raise HTTPException(status_code=400, detail="The uploaded .xlsx file signature is invalid.")
        try:
            with zipfile.ZipFile(BytesIO(content)) as archive:
                if any(Path(name).is_absolute() or ".." in Path(name).parts for name in archive.namelist()):
                    raise HTTPException(status_code=400, detail="Workbook archive contains an unsafe path.")
                if any(name.lower().endswith("vbaproject.bin") for name in archive.namelist()) and os.getenv("ALLOW_MACRO_FILES", "false").lower() != "true":
                    raise HTTPException(status_code=400, detail="Macro-enabled workbooks are not accepted.")
        except zipfile.BadZipFile as exc:
            raise HTTPException(status_code=400, detail="The uploaded .xlsx archive is invalid.") from exc
    return extension


def scan_file(path: Path) -> None:
    """Scan a quarantined file when configured; fail closed if scanning is required."""
    enabled = os.getenv("CLAMAV_SCAN_ENABLED", "false").lower() == "true"
    required = os.getenv("CLAMAV_SCAN_REQUIRED", "false").lower() == "true"
    if not enabled:
        if required:
            raise HTTPException(status_code=503, detail="Upload antivirus scanning is required but not enabled.")
        return
    scanner = shutil.which("clamdscan") or shutil.which("clamscan")
    if not scanner:
        raise HTTPException(status_code=503, detail="Upload antivirus scanner is unavailable.")
    result = subprocess.run([scanner, "--no-summary", str(path)], capture_output=True, text=True, timeout=30, check=False)
    if result.returncode != 0:
        raise HTTPException(status_code=400, detail="Upload rejected by antivirus scanning.")
