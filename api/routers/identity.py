"""Enterprise role login and channel-based account recovery endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas.chatbot import TokenResponse
from api.schemas.identity import RecoveryConfirmRequest, RecoveryConfirmResponse, RecoveryRequest, RecoveryRequestResponse, RoleLoginRequest
from api.services.identity_service import confirm_recovery, request_recovery, role_login
from database.config import get_db


router = APIRouter(prefix="/api/v1/identity", tags=["identity"])


@router.post("/login", response_model=TokenResponse, summary="Role-aware portal login", description="Authenticates only when the selected admin/client portal matches the user's database role.")
async def login(payload: RoleLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return role_login(db, payload)


@router.post("/recovery/request", response_model=RecoveryRequestResponse, summary="Request account recovery", description="Returns a generic response and sends a rate-limited, ten-minute code through an eligible verified channel.")
async def recovery_request(payload: RecoveryRequest, db: Session = Depends(get_db)) -> RecoveryRequestResponse:
    request_recovery(db, payload)
    return RecoveryRequestResponse()


@router.post("/recovery/confirm", response_model=RecoveryConfirmResponse, summary="Confirm account recovery", description="Consumes a single-use code, changes the password, revokes active sessions, and records a security event.")
async def recovery_confirm(payload: RecoveryConfirmRequest, db: Session = Depends(get_db)) -> RecoveryConfirmResponse:
    confirm_recovery(db, payload)
    return RecoveryConfirmResponse(success=True, message="Password reset successfully. Sign in again.")
