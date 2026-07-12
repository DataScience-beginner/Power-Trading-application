"""SaaS authentication and admin-led user onboarding routes."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from api.schemas.chatbot import AdminRecoveryRequest, BootstrapAdminRequest, LoginRequest, PasswordChangeRequest, PasswordOperationResponse, TokenResponse, UserCreateRequest, UserResponse
from api.security.ai_foundation import require_ai_foundation_access
from api.security.chat_auth import clear_auth_cookie, create_access_token, get_current_user, require_admin, set_auth_cookie
from api.services.chat_auth_service import authenticate, bootstrap_admin, change_password, create_user, recover_platform_admin, user_response
from database.chatbot_models import AppUser
from database.config import get_db


router = APIRouter(prefix="/api/v1/auth", tags=["saas-auth"])


@router.post(
    "/bootstrap-admin",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bootstrap first platform administrator",
    description="Creates the first admin using the internal service credential; disabled after an admin exists.",
)
async def bootstrap_first_admin(
    payload: BootstrapAdminRequest,
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> UserResponse:
    return user_response(db, bootstrap_admin(db, payload))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login to Innowatt workspace",
    description="Authenticates an active SaaS user and returns a signed role-aware access token.",
)
async def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate(db, str(payload.email), payload.password)
    token, expires_at = create_access_token(user, db=db)
    db.commit()
    set_auth_cookie(response, token, expires_at)
    return TokenResponse(access_token=token, expires_at=expires_at, user=user_response(db, user))


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get authenticated user",
    description="Returns current role and authorized client/portfolio scope from database state.",
)
async def me(user: AppUser = Depends(get_current_user), db: Session = Depends(get_db)) -> UserResponse:
    return user_response(db, user)


@router.post(
    "/logout",
    response_model=PasswordOperationResponse,
    summary="Logout and revoke active sessions",
    description="Clears the secure browser cookie and revokes active server-side sessions for the authenticated user.",
)
async def logout(response: Response, user: AppUser = Depends(get_current_user), db: Session = Depends(get_db)) -> PasswordOperationResponse:
    from datetime import UTC, datetime
    from database.identity_models import AuthSession

    db.query(AuthSession).filter(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None)).update(
        {"revoked_at": datetime.now(UTC).replace(tzinfo=None)}
    )
    db.commit()
    clear_auth_cookie(response)
    return PasswordOperationResponse(success=True, message="Signed out successfully.")


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create SaaS user",
    description="Allows a platform admin to create another admin or a client/portfolio-scoped user.",
)
async def register_user(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    _admin: AppUser = Depends(require_admin),
) -> UserResponse:
    return user_response(db, create_user(db, payload))


@router.post(
    "/change-password",
    response_model=PasswordOperationResponse,
    summary="Change authenticated user password",
    description="Verifies the current password before replacing it with a new one-way hash.",
)
async def update_own_password(
    payload: PasswordChangeRequest,
    db: Session = Depends(get_db),
    user: AppUser = Depends(get_current_user),
) -> PasswordOperationResponse:
    change_password(db, user, payload)
    return PasswordOperationResponse(success=True, message="Password changed successfully. Sign in again on other devices.")


@router.post(
    "/recover-admin",
    response_model=PasswordOperationResponse,
    summary="Recover platform administrator password",
    description="Allows locked-out founder recovery using the internal AI Foundation service credential; never returns password hashes.",
)
async def recover_admin_password(
    payload: AdminRecoveryRequest,
    db: Session = Depends(get_db),
    _access: str = Depends(require_ai_foundation_access),
) -> PasswordOperationResponse:
    recover_platform_admin(db, payload)
    return PasswordOperationResponse(success=True, message="Administrator password reset. You can now sign in.")
