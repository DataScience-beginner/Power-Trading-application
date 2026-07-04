from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from excel_consumption_service.models.base import Base, IdentifierMixin, TimestampMixin


class WorkbookUpload(IdentifierMixin, TimestampMixin, Base):
    """Metadata for one uploaded workbook and its processing lifecycle."""

    __tablename__ = "workbook_uploads"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), index=True)
    uploaded_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    original_file_name: Mapped[str] = mapped_column(String(255))
    stored_file_path: Mapped[str | None] = mapped_column(String(255))
    workbook_month: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(40), default="uploaded")


class SheetIngestion(IdentifierMixin, TimestampMixin, Base):
    """Processing state for each source sheet extracted from a workbook."""

    __tablename__ = "sheet_ingestions"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    workbook_upload_id: Mapped[str] = mapped_column(
        ForeignKey("workbook_uploads.id"),
        index=True,
    )
    sheet_name: Mapped[str] = mapped_column(String(120))
    sheet_type: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(40), default="pending")
    row_count: Mapped[int | None] = mapped_column(Integer)
    validation_summary: Mapped[str | None] = mapped_column(Text)


class SourceIntervalRecord(IdentifierMixin, TimestampMixin, Base):
    """Normalized time-block input such as DAM and RTM daily interval data."""

    __tablename__ = "source_interval_records"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    workbook_upload_id: Mapped[str] = mapped_column(
        ForeignKey("workbook_uploads.id"),
        index=True,
    )
    source_type: Mapped[str] = mapped_column(String(40))
    reading_date: Mapped[date] = mapped_column(Date, index=True)
    time_block_label: Mapped[str] = mapped_column(String(40))
    category_code: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[float] = mapped_column(Float)


class DailyConsumptionRecord(IdentifierMixin, TimestampMixin, Base):
    """Normalized daily input such as TNEB values and category totals."""

    __tablename__ = "daily_consumption_records"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    workbook_upload_id: Mapped[str] = mapped_column(
        ForeignKey("workbook_uploads.id"),
        index=True,
    )
    source_type: Mapped[str] = mapped_column(String(40))
    reading_date: Mapped[date] = mapped_column(Date, index=True)
    metric_name: Mapped[str] = mapped_column(String(60))
    category_code: Mapped[str | None] = mapped_column(String(20))
    value: Mapped[float] = mapped_column(Float)


class SolarDailyRecord(IdentifierMixin, TimestampMixin, Base):
    """Future normalized solar sheet records once direct solar uploads are enabled."""

    __tablename__ = "solar_daily_records"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    workbook_upload_id: Mapped[str] = mapped_column(
        ForeignKey("workbook_uploads.id"),
        index=True,
    )
    reading_date: Mapped[date] = mapped_column(Date, index=True)
    metric_name: Mapped[str] = mapped_column(String(60))
    value: Mapped[float] = mapped_column(Float)


class CalculationRun(IdentifierMixin, TimestampMixin, Base):
    """Audit record for one deterministic calculation execution."""

    __tablename__ = "calculation_runs"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    workbook_upload_id: Mapped[str] = mapped_column(
        ForeignKey("workbook_uploads.id"),
        index=True,
    )
    calculation_type: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(40), default="pending")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str | None] = mapped_column(Text)


class SolarWorkingResult(IdentifierMixin, TimestampMixin, Base):
    """Daily backend-generated output replacing the workbook's Solar Working formulas."""

    __tablename__ = "solar_working_results"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    workbook_upload_id: Mapped[str] = mapped_column(
        ForeignKey("workbook_uploads.id"),
        index=True,
    )
    reading_date: Mapped[date] = mapped_column(Date, index=True)
    tneb_c1: Mapped[float] = mapped_column(Float, default=0)
    tneb_c2: Mapped[float] = mapped_column(Float, default=0)
    tneb_c4: Mapped[float] = mapped_column(Float, default=0)
    tneb_c5: Mapped[float] = mapped_column(Float, default=0)
    tneb_total: Mapped[float] = mapped_column(Float, default=0)
    iex_c1: Mapped[float] = mapped_column(Float, default=0)
    iex_c2: Mapped[float] = mapped_column(Float, default=0)
    iex_c4: Mapped[float] = mapped_column(Float, default=0)
    iex_c5: Mapped[float] = mapped_column(Float, default=0)
    iex_total: Mapped[float] = mapped_column(Float, default=0)
    post_iex_balance: Mapped[float] = mapped_column(Float, default=0)
    solar_total: Mapped[float] = mapped_column(Float, default=0)
    tneb_balance: Mapped[float] = mapped_column(Float, default=0)
    banking_balance: Mapped[float] = mapped_column(Float, default=0)
