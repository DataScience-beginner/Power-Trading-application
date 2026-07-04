"""Import model classes so SQLAlchemy metadata is complete during startup."""

from excel_consumption_service.models.auth import Role, User, UserRoleAssignment
from excel_consumption_service.models.base import Base
from excel_consumption_service.models.tenant import Site, Tenant
from excel_consumption_service.models.workbook import (
    CalculationRun,
    DailyConsumptionRecord,
    SheetIngestion,
    SolarDailyRecord,
    SolarWorkingResult,
    SourceIntervalRecord,
    WorkbookUpload,
)

__all__ = [
    "Base",
    "CalculationRun",
    "DailyConsumptionRecord",
    "Role",
    "SheetIngestion",
    "Site",
    "SolarDailyRecord",
    "SolarWorkingResult",
    "SourceIntervalRecord",
    "Tenant",
    "User",
    "UserRoleAssignment",
    "WorkbookUpload",
]
