from pathlib import Path
from uuid import uuid4

from excel_consumption_service.core.config import get_settings


def store_uploaded_workbook(file_name: str, content: bytes) -> str:
    """Persist the uploaded workbook under the configured upload directory."""

    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file_name).suffix or ".xlsx"
    stored_name = f"{uuid4()}{suffix}"
    target_path = upload_dir / stored_name
    target_path.write_bytes(content)
    return str(target_path)
