from sqlalchemy import select
from sqlalchemy.orm import Session

from excel_consumption_service.models.tenant import Site
from excel_consumption_service.models.workbook import (
    DailyConsumptionRecord,
    SheetIngestion,
    SolarDailyRecord,
    SourceIntervalRecord,
    WorkbookUpload,
)
from excel_consumption_service.schemas.auth import AuthenticatedUser
from excel_consumption_service.schemas.workbook import (
    ParsedSheetSummary,
    SolarWorkingRow,
    WorkbookResultsResponse,
    WorkbookUploadResponse,
)
from excel_consumption_service.services.file_storage import store_uploaded_workbook
from excel_consumption_service.services.solar_working import (
    SolarWorkingInputs,
    calculate_solar_working,
    load_solar_working_rows,
)
from excel_consumption_service.services.workbook_parser import parse_workbook


def ingest_uploaded_workbook(
    db: Session,
    current_user: AuthenticatedUser,
    file_name: str,
    content: bytes,
) -> WorkbookUploadResponse:
    """Store, parse, persist, and calculate one uploaded workbook."""

    if current_user.tenant_id is None:
        raise ValueError("Current user is not scoped to a tenant.")

    stored_path = store_uploaded_workbook(file_name=file_name, content=content)
    parsed = parse_workbook(file_name=file_name, content=content)
    site = _resolve_default_site(db=db, tenant_id=current_user.tenant_id)

    workbook_upload = WorkbookUpload(
        tenant_id=current_user.tenant_id,
        site_id=site.id if site else None,
        uploaded_by_user_id=current_user.id,
        original_file_name=file_name,
        stored_file_path=stored_path,
        workbook_month=parsed.workbook_month,
        status="processing",
    )
    db.add(workbook_upload)
    db.flush()

    _persist_parsed_records(db=db, workbook_upload=workbook_upload, parsed=parsed)
    calculation_summary = calculate_solar_working(
        db=db,
        inputs=SolarWorkingInputs(
            tenant_id=workbook_upload.tenant_id,
            workbook_id=workbook_upload.id,
        ),
    )

    workbook_upload.status = "calculated"
    db.commit()
    db.refresh(workbook_upload)

    preview_rows = load_solar_working_rows(db=db, workbook_id=workbook_upload.id, limit=10)
    return WorkbookUploadResponse(
        workbook_id=workbook_upload.id,
        file_name=workbook_upload.original_file_name,
        workbook_month=workbook_upload.workbook_month,
        status=workbook_upload.status,
        sheet_summaries=[
            ParsedSheetSummary(
                sheet_name=item.sheet_name,
                sheet_type=item.sheet_type,
                status=item.status,
                row_count=item.row_count,
                validation_summary=item.validation_summary,
            )
            for item in parsed.sheet_summaries
        ],
        calculation_summary=calculation_summary,
        preview_rows=[
            SolarWorkingRow(
                reading_date=row.reading_date.isoformat(),
                tneb_total=row.tneb_total,
                iex_total=row.iex_total,
                solar_total=row.solar_total,
                tneb_balance=row.tneb_balance,
                banking_balance=row.banking_balance,
            )
            for row in preview_rows
        ],
    )


def get_workbook_results(
    db: Session,
    workbook_id: str,
    current_user: AuthenticatedUser,
) -> WorkbookResultsResponse:
    """Load calculated rows for one uploaded workbook."""

    workbook_upload = db.scalar(
        select(WorkbookUpload).where(WorkbookUpload.id == workbook_id)
    )
    if workbook_upload is None:
        raise ValueError("Workbook not found.")
    _assert_workbook_access(
        workbook_tenant_id=workbook_upload.tenant_id,
        current_user=current_user,
    )

    rows = load_solar_working_rows(db=db, workbook_id=workbook_id, limit=None)
    return WorkbookResultsResponse(
        workbook_id=workbook_upload.id,
        workbook_month=workbook_upload.workbook_month,
        status=workbook_upload.status,
        rows=[
            SolarWorkingRow(
                reading_date=row.reading_date.isoformat(),
                tneb_total=row.tneb_total,
                iex_total=row.iex_total,
                solar_total=row.solar_total,
                tneb_balance=row.tneb_balance,
                banking_balance=row.banking_balance,
            )
            for row in rows
        ],
    )


def _resolve_default_site(db: Session, tenant_id: str | None) -> Site | None:
    if tenant_id is None:
        return None
    return db.scalar(select(Site).where(Site.tenant_id == tenant_id).limit(1))


def _persist_parsed_records(db: Session, workbook_upload: WorkbookUpload, parsed) -> None:
    for summary in parsed.sheet_summaries:
        db.add(
            SheetIngestion(
                tenant_id=workbook_upload.tenant_id,
                workbook_upload_id=workbook_upload.id,
                sheet_name=summary.sheet_name,
                sheet_type=summary.sheet_type,
                status=summary.status,
                row_count=summary.row_count,
                validation_summary=summary.validation_summary,
            )
        )

    db.add_all(
        [
            SourceIntervalRecord(
                tenant_id=workbook_upload.tenant_id,
                workbook_upload_id=workbook_upload.id,
                source_type=item.source_type,
                reading_date=item.reading_date,
                time_block_label=item.time_block_label,
                category_code=item.category_code,
                quantity=item.quantity,
            )
            for item in parsed.interval_records
        ]
    )
    db.add_all(
        [
            DailyConsumptionRecord(
                tenant_id=workbook_upload.tenant_id,
                workbook_upload_id=workbook_upload.id,
                source_type=item.source_type,
                reading_date=item.reading_date,
                metric_name=item.metric_name,
                category_code=item.category_code,
                value=item.value,
            )
            for item in parsed.daily_values
        ]
    )
    db.add_all(
        [
            SolarDailyRecord(
                tenant_id=workbook_upload.tenant_id,
                workbook_upload_id=workbook_upload.id,
                reading_date=item.reading_date,
                metric_name=item.metric_name,
                value=item.value,
            )
            for item in parsed.solar_values
        ]
    )
    db.flush()


def _assert_workbook_access(
    workbook_tenant_id: str,
    current_user: AuthenticatedUser,
) -> None:
    """Enforce tenant isolation while still allowing platform admins to inspect all tenants."""

    if "platform_admin" in current_user.role_codes:
        return
    if current_user.tenant_id != workbook_tenant_id:
        raise ValueError("Workbook not found.")
