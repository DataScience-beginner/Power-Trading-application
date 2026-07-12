"""Enterprise role login and channel-based account recovery endpoints."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from api.schemas.chatbot import TokenResponse
from api.schemas.identity import MfaEnrollmentResponse, MfaVerifyRequest, MfaVerifyResponse, OnboardingInviteRequest, OnboardingInviteResponse, OnboardingStatusResponse, OnboardingVerifyRequest, OnboardingVerifyResponse, RecoveryConfirmRequest, RecoveryConfirmResponse, RecoveryRequest, RecoveryRequestResponse, RoleLoginRequest
from api.security.chat_auth import get_current_user, require_admin, set_auth_cookie
from api.services.identity_service import begin_mfa_enrollment, confirm_recovery, invite_client, onboarding_status, request_recovery, role_login, verify_mfa_enrollment, verify_onboarding
from database.chatbot_models import AppUser
from database.config import get_db


router = APIRouter(prefix="/api/v1/identity", tags=["identity"])


@router.post("/login", response_model=TokenResponse, summary="Role-aware portal login", description="Authenticates only when the selected admin/client portal matches the user's database role.")
async def login(payload: RoleLoginRequest, response: Response, db: Session = Depends(get_db)) -> TokenResponse:
    result = role_login(db, payload)
    set_auth_cookie(response, result.access_token, result.expires_at)
    return result


@router.post("/mfa/enroll", response_model=MfaEnrollmentResponse, summary="Begin TOTP MFA enrollment", description="Creates an encrypted TOTP factor and returns its secret once to the authenticated user for authenticator setup.")
async def mfa_enroll(db: Session = Depends(get_db), user: AppUser = Depends(get_current_user)) -> MfaEnrollmentResponse:
    return begin_mfa_enrollment(db, user)


@router.post("/mfa/verify", response_model=MfaVerifyResponse, summary="Verify and enable TOTP MFA", description="Verifies an authenticator code, enables MFA, and returns single-use recovery codes once.")
async def mfa_verify(payload: MfaVerifyRequest, db: Session = Depends(get_db), user: AppUser = Depends(get_current_user)) -> MfaVerifyResponse:
    return verify_mfa_enrollment(db, user, payload.code)


@router.post("/recovery/request", response_model=RecoveryRequestResponse, summary="Request account recovery", description="Returns a generic response and sends a rate-limited, ten-minute code through an eligible verified channel.")
async def recovery_request(payload: RecoveryRequest, db: Session = Depends(get_db)) -> RecoveryRequestResponse:
    request_recovery(db, payload)
    return RecoveryRequestResponse()


@router.post("/recovery/confirm", response_model=RecoveryConfirmResponse, summary="Confirm account recovery", description="Consumes a single-use code, changes the password, revokes active sessions, and records a security event.")
async def recovery_confirm(payload: RecoveryConfirmRequest, db: Session = Depends(get_db)) -> RecoveryConfirmResponse:
    confirm_recovery(db, payload)
    return RecoveryConfirmResponse(success=True, message="Password reset successfully. Sign in again.")


@router.post("/onboarding/invite", response_model=OnboardingInviteResponse, status_code=201, summary="Invite a client user", description="Creates an inactive client-scoped identity and sends mock or configured email/SMS verification challenges.")
async def onboarding_invite(payload: OnboardingInviteRequest, db: Session = Depends(get_db), _admin: AppUser = Depends(require_admin)) -> OnboardingInviteResponse:
    return invite_client(db, payload)


@router.post("/onboarding/verify", response_model=OnboardingVerifyResponse, summary="Verify onboarding channel", description="Consumes a single-use email or SMS challenge, sets the initial password, and activates the user after required channels pass.")
async def onboarding_verify(payload: OnboardingVerifyRequest, db: Session = Depends(get_db)) -> OnboardingVerifyResponse:
    return verify_onboarding(db, payload)


@router.get("/onboarding/{user_id}", response_model=OnboardingStatusResponse, summary="Get onboarding status", description="Returns non-secret verification and activation status for an onboarding identity.")
async def onboarding_status_route(user_id: str, db: Session = Depends(get_db), _admin: AppUser = Depends(require_admin)) -> OnboardingStatusResponse:
    return onboarding_status(db, user_id)
