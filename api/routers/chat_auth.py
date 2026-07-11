"""SaaS authentication and admin-led user onboarding routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.schemas.chatbot import BootstrapAdminRequest, LoginRequest, TokenResponse, UserCreateRequest, UserResponse
from api.security.ai_foundation import require_ai_foundation_access
from api.security.chat_auth import create_access_token, get_current_user, require_admin
from api.services.chat_auth_service import authenticate, bootstrap_admin, create_user, user_response
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
async def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate(db, str(payload.email), payload.password)
    token, expires_at = create_access_token(user)
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
