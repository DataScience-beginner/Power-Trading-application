from pydantic import BaseModel


class WorkbookListItem(BaseModel):
    """Summary item for workbook history lists."""

    workbook_id: str
    file_name: str
    workbook_month: str | None
    status: str
    uploaded_at: str
    uploaded_by_user_id: str | None
    solar_working_rows: int


class AdminOverviewMetric(BaseModel):
    """Simple label/value pair for admin overview dashboards."""

    label: str
    value: int


class AdminOverviewResponse(BaseModel):
    """Operational dashboard payload for admins."""

    metrics: list[AdminOverviewMetric]
    recent_workbooks: list[WorkbookListItem]
    tenant_codes: list[str]
    user_emails: list[str]
