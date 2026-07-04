from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from excel_consumption_service.api.dependencies.auth import get_current_user, require_roles
from excel_consumption_service.db.session import get_db
from excel_consumption_service.schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    LoginResponse,
)
from excel_consumption_service.schemas.dashboard import AdminOverviewResponse
from excel_consumption_service.services.admin_dashboard import get_admin_overview
from excel_consumption_service.services.authentication import authenticate_and_issue_token


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Authenticate the user and return a token plus role-aware profile details."""

    return authenticate_and_issue_token(db=db, payload=payload)


@router.get("/me", response_model=AuthenticatedUser)
def me(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    """Return the authenticated user profile for the current token."""

    return current_user


@router.get("/admin/summary")
def admin_summary(
    current_user: AuthenticatedUser = Depends(
        require_roles("platform_admin", "tenant_admin")
    ),
) -> dict[str, object]:
    """Admin-only placeholder endpoint for the future management console."""

    return {
        "portal": "admin",
        "user": current_user.model_dump(),
        "capabilities": [
            "tenant management",
            "service monitoring",
            "upload oversight",
            "rbac administration",
        ],
    }


@router.get("/admin/overview", response_model=AdminOverviewResponse)
def admin_overview(
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("platform_admin", "tenant_admin")
    ),
) -> AdminOverviewResponse:
    """Return operational data for the admin dashboard."""

    return get_admin_overview(db=db, current_user=current_user)


@router.get("/client/summary")
def client_summary(
    current_user: AuthenticatedUser = Depends(
        require_roles("platform_admin", "tenant_admin", "client_viewer")
    ),
) -> dict[str, object]:
    """Client-facing placeholder endpoint for the tenant dashboard."""

    return {
        "portal": "client",
        "user": current_user.model_dump(),
        "capabilities": [
            "workbook upload",
            "solar working review",
            "calculation history",
            "site dashboards",
        ],
    }
