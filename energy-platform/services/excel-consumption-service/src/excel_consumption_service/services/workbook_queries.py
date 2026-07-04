from sqlalchemy import func, select
from sqlalchemy.orm import Session

from excel_consumption_service.models.workbook import SolarWorkingResult, WorkbookUpload
from excel_consumption_service.schemas.auth import AuthenticatedUser
from excel_consumption_service.schemas.dashboard import WorkbookListItem


def list_workbooks(
    db: Session,
    current_user: AuthenticatedUser,
) -> list[WorkbookListItem]:
    """Return workbook history filtered by the caller's tenant scope."""

    statement = (
        select(
            WorkbookUpload,
            func.count(SolarWorkingResult.id).label("solar_working_rows"),
        )
        .outerjoin(
            SolarWorkingResult,
            SolarWorkingResult.workbook_upload_id == WorkbookUpload.id,
        )
        .group_by(WorkbookUpload.id)
        .order_by(WorkbookUpload.created_at.desc())
    )
    if "platform_admin" not in current_user.role_codes:
        statement = statement.where(WorkbookUpload.tenant_id == current_user.tenant_id)

    rows = db.execute(statement).all()
    return [
        WorkbookListItem(
            workbook_id=workbook.id,
            file_name=workbook.original_file_name,
            workbook_month=workbook.workbook_month,
            status=workbook.status,
            uploaded_at=workbook.created_at.isoformat(),
            uploaded_by_user_id=workbook.uploaded_by_user_id,
            solar_working_rows=solar_working_rows,
        )
        for workbook, solar_working_rows in rows
    ]
