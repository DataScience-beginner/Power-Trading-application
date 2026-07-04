from sqlalchemy import func, select
from sqlalchemy.orm import Session

from excel_consumption_service.models.auth import User
from excel_consumption_service.models.tenant import Tenant
from excel_consumption_service.models.workbook import WorkbookUpload
from excel_consumption_service.schemas.auth import AuthenticatedUser
from excel_consumption_service.schemas.dashboard import (
    AdminOverviewMetric,
    AdminOverviewResponse,
)
from excel_consumption_service.services.workbook_queries import list_workbooks


def get_admin_overview(
    db: Session,
    current_user: AuthenticatedUser,
) -> AdminOverviewResponse:
    """Build a compact operational snapshot for the admin dashboard."""

    workbook_items = list_workbooks(db=db, current_user=current_user)[:10]

    tenant_statement = select(func.count()).select_from(Tenant)
    user_statement = select(func.count()).select_from(User)
    workbook_statement = select(func.count()).select_from(WorkbookUpload)

    tenant_codes_statement = select(Tenant.code).order_by(Tenant.code)
    user_emails_statement = select(User.email).order_by(User.email)

    if "platform_admin" not in current_user.role_codes:
        tenant_statement = tenant_statement.where(Tenant.id == current_user.tenant_id)
        user_statement = user_statement.where(User.tenant_id == current_user.tenant_id)
        workbook_statement = workbook_statement.where(
            WorkbookUpload.tenant_id == current_user.tenant_id
        )
        tenant_codes_statement = tenant_codes_statement.where(
            Tenant.id == current_user.tenant_id
        )
        user_emails_statement = user_emails_statement.where(
            User.tenant_id == current_user.tenant_id
        )

    metrics = [
        AdminOverviewMetric(label="Tenants", value=db.scalar(tenant_statement) or 0),
        AdminOverviewMetric(label="Users", value=db.scalar(user_statement) or 0),
        AdminOverviewMetric(
            label="Workbook Uploads",
            value=db.scalar(workbook_statement) or 0,
        ),
    ]

    return AdminOverviewResponse(
        metrics=metrics,
        recent_workbooks=workbook_items,
        tenant_codes=list(db.scalars(tenant_codes_statement)),
        user_emails=list(db.scalars(user_emails_statement)),
    )
