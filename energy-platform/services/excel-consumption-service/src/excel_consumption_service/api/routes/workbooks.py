from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from excel_consumption_service.api.dependencies.auth import require_roles
from excel_consumption_service.db.session import get_db
from excel_consumption_service.schemas.auth import AuthenticatedUser
from excel_consumption_service.schemas.dashboard import WorkbookListItem
from excel_consumption_service.schemas.workbook import (
    WorkbookResultsResponse,
    WorkbookUploadResponse,
)
from excel_consumption_service.services.workbook_ingestion import (
    get_workbook_results,
    ingest_uploaded_workbook,
)
from excel_consumption_service.services.workbook_queries import list_workbooks


router = APIRouter(prefix="/api/v1/workbooks", tags=["workbooks"])


@router.post("/upload", response_model=WorkbookUploadResponse)
async def upload_workbook(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("platform_admin", "tenant_admin", "client_viewer")
    ),
) -> WorkbookUploadResponse:
    """Accept a workbook upload and immediately process it."""

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required.",
        )
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .xlsx workbooks are supported.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        return ingest_uploaded_workbook(
            db=db,
            current_user=current_user,
            file_name=file.filename,
            content=content,
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("", response_model=list[WorkbookListItem])
def read_workbook_history(
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("platform_admin", "tenant_admin", "client_viewer")
    ),
) -> list[WorkbookListItem]:
    """Return workbook history within the caller's tenant scope."""

    return list_workbooks(db=db, current_user=current_user)


@router.get("/{workbook_id}/solar-working", response_model=WorkbookResultsResponse)
def read_solar_working_results(
    workbook_id: str,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(
        require_roles("platform_admin", "tenant_admin", "client_viewer")
    ),
) -> WorkbookResultsResponse:
    """Read the calculated Solar Working rows for one workbook."""

    try:
        return get_workbook_results(
            db=db,
            workbook_id=workbook_id,
            current_user=_,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
