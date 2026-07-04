from fastapi import APIRouter

from excel_consumption_service.api.routes.auth import router as auth_router
from excel_consumption_service.api.routes.system import router as system_router
from excel_consumption_service.api.routes.workbooks import router as workbook_router


# The API root keeps route registration centralized so service growth stays readable.
router = APIRouter()
router.include_router(system_router)
router.include_router(auth_router)
router.include_router(workbook_router)
