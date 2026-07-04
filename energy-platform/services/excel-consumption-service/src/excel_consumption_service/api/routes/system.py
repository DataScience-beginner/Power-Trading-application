from fastapi import APIRouter

from excel_consumption_service.core.config import get_settings


router = APIRouter(tags=["system"])
settings = get_settings()


@router.get("/")
def root() -> dict[str, str]:
    return {
        "service": settings.service_name,
        "status": "ok",
        "message": "Excel consumption service is running.",
    }


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "service": settings.service_name,
        "environment": settings.environment,
        "status": "healthy",
    }


@router.get("/api/v1/service-info")
def service_info() -> dict[str, object]:
    return {
        "service_key": "excel-consumption-service",
        "database_url": settings.database_url,
        "upload_dir": settings.upload_dir,
        "default_tenant": settings.default_tenant,
        "next_capabilities": [
            "workbook upload",
            "sheet parsing",
            "tenant-scoped storage",
            "solar working calculation",
            "rbac-enabled operations",
        ],
    }
