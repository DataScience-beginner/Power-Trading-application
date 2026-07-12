"""Administrative security posture, identity configuration, and audit routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.schemas.security_governance import DevicePolicyResponse, EnterpriseIdentityStatus, SecurityAuditExportResponse, SecurityPostureResponse
from api.security.chat_auth import require_admin
from api.services.security_governance_service import device_policy, enterprise_identity_status, export_security_events, security_posture
from database.chatbot_models import AppUser
from database.config import get_db


router = APIRouter(prefix="/api/v1/security", tags=["security-governance"])


@router.get("/posture", response_model=SecurityPostureResponse, summary="Read security-control posture", description="Returns non-secret activation status and dependencies for application, edge, identity, and upload controls.")
async def read_security_posture(_admin: AppUser = Depends(require_admin)) -> SecurityPostureResponse:
    return security_posture()


@router.get("/enterprise-identity", response_model=EnterpriseIdentityStatus, summary="Read enterprise identity integration status", description="Reports whether OIDC, SAML, SCIM, and passkey integration settings are configured without exposing their secrets.")
async def read_enterprise_identity(_admin: AppUser = Depends(require_admin)) -> EnterpriseIdentityStatus:
    return enterprise_identity_status()


@router.get("/device-policy", response_model=DevicePolicyResponse, summary="Read device and session policy", description="Returns effective managed-device, email-domain, session lifetime, and administrator MFA policy.")
async def read_device_policy(_admin: AppUser = Depends(require_admin)) -> DevicePolicyResponse:
    return device_policy()


@router.get("/audit/events", response_model=SecurityAuditExportResponse, summary="Export security audit events", description="Returns a bounded administrator-only JSON export for SIEM ingestion and compliance evidence.")
async def read_security_events(limit: int = Query(1000, ge=1, le=5000), db: Session = Depends(get_db), _admin: AppUser = Depends(require_admin)) -> SecurityAuditExportResponse:
    return export_security_events(db, limit)
