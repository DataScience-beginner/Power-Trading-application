from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from excel_consumption_service.core.security import (
    TokenPayload,
    create_access_token,
    decode_access_token as decode_token_payload,
    verify_password,
)
from excel_consumption_service.models.auth import User, UserRoleAssignment
from excel_consumption_service.schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    LoginResponse,
)


PORTAL_ROLES = {
    "admin": {"platform_admin", "tenant_admin"},
    "client": {"platform_admin", "tenant_admin", "client_viewer"},
}


def authenticate_and_issue_token(db: Session, payload: LoginRequest) -> LoginResponse:
    """Authenticate a user and enforce that they can access the selected portal."""

    user = db.scalar(
        select(User)
        .options(
            selectinload(User.role_assignments).selectinload(
                UserRoleAssignment.role
            )
        )
        .where(User.email == payload.email)
    )
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    role_codes = [assignment.role.code for assignment in user.role_assignments]
    if not set(role_codes).intersection(PORTAL_ROLES[payload.portal]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User cannot access the {payload.portal} portal.",
        )

    authenticated_user = AuthenticatedUser(
        id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        full_name=user.full_name,
        role_codes=sorted(role_codes),
    )
    return LoginResponse(
        access_token=create_access_token(subject=user.id),
        user=authenticated_user,
    )


def decode_access_token(token: str) -> TokenPayload:
    """Small wrapper to keep token decoding concerns in one service module."""

    try:
        return decode_token_payload(token)
    except Exception as exc:  # pragma: no cover - broad here keeps API errors simple
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        ) from exc


def get_authenticated_user(db: Session, user_id: str) -> AuthenticatedUser:
    """Load the current user and normalize role data for API responses."""

    user = db.scalar(
        select(User)
        .options(
            selectinload(User.role_assignments).selectinload(
                UserRoleAssignment.role
            )
        )
        .where(User.id == user_id)
    )
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user is no longer active.",
        )

    return AuthenticatedUser(
        id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        full_name=user.full_name,
        role_codes=sorted(
            assignment.role.code for assignment in user.role_assignments
        ),
    )
