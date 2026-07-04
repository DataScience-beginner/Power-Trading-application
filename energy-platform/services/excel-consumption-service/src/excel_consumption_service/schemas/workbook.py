from pydantic import BaseModel


class ParsedSheetSummary(BaseModel):
    """Small summary of how one sheet was handled during ingestion."""

    sheet_name: str
    sheet_type: str
    status: str
    row_count: int | None = None
    validation_summary: str | None = None


class SolarWorkingRow(BaseModel):
    """API shape for one calculated Solar Working row."""

    reading_date: str
    tneb_total: float
    iex_total: float
    solar_total: float
    tneb_balance: float
    banking_balance: float


class WorkbookUploadResponse(BaseModel):
    """Response sent after upload, parse, persistence, and calculation."""

    workbook_id: str
    file_name: str
    workbook_month: str | None = None
    status: str
    sheet_summaries: list[ParsedSheetSummary]
    calculation_summary: dict[str, object]
    preview_rows: list[SolarWorkingRow]


class WorkbookResultsResponse(BaseModel):
    """Response for reading back one workbook's calculated output."""

    workbook_id: str
    workbook_month: str | None = None
    status: str
    rows: list[SolarWorkingRow]
