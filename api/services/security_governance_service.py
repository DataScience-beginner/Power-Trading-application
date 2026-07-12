"""Security posture reporting and bounded audit evidence services."""

from datetime import UTC, datetime
import os

from sqlalchemy.orm import Session

from api.schemas.security_governance import ControlStatus, DevicePolicyResponse, EnterpriseIdentityStatus, SecurityAuditExportResponse, SecurityEventItem, SecurityPostureResponse
from database.identity_models import SecurityEvent


def _enabled(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default).lower()).lower() == "true"


def security_posture() -> SecurityPostureResponse:
    controls = [
        ControlStatus(control="rate_limits", status="active" if _enabled("RATE_LIMIT_ENABLED", True) else "disabled", evidence="ApiSecurityMiddleware"),
        ControlStatus(control="secure_cookies", status="active" if _enabled("AUTH_COOKIE_ENABLED", True) else "disabled", evidence="HttpOnly/Secure/SameSite session cookie"),
        ControlStatus(control="admin_mfa", status="active" if _enabled("MFA_REQUIRED_FOR_ADMIN") else "available", evidence="Encrypted RFC 6238 TOTP factors"),
        ControlStatus(control="upload_antivirus", status="active" if _enabled("CLAMAV_SCAN_ENABLED") else "integration_ready", evidence="Quarantine and scanner adapter", activation_dependency="Install ClamAV or select managed scanner"),
        ControlStatus(control="waf", status="active" if _enabled("WAF_VERIFICATION_REQUIRED") else "integration_ready", evidence="Fail-closed edge verification header", activation_dependency="Configure WAF secret/header injection"),
        ControlStatus(control="enterprise_sso", status="configured" if os.getenv("OIDC_ISSUER_URL") else "integration_ready", evidence="Environment-scoped OIDC/SAML/SCIM contract", activation_dependency="Customer identity-provider metadata"),
    ]
    required = {item.control: item.status for item in controls}
    ready = all(required[name] == "active" for name in ("rate_limits", "secure_cookies", "admin_mfa", "upload_antivirus", "waf"))
    return SecurityPostureResponse(environment=os.getenv("ENVIRONMENT", "development"), controls=controls, production_ready=ready)


def enterprise_identity_status() -> EnterpriseIdentityStatus:
    return EnterpriseIdentityStatus(
        oidc_configured=bool(os.getenv("OIDC_ISSUER_URL") and os.getenv("OIDC_CLIENT_ID")),
        saml_configured=bool(os.getenv("SAML_METADATA_URL") or os.getenv("SAML_METADATA_XML")),
        scim_configured=bool(os.getenv("SCIM_BEARER_TOKEN")),
        passkeys_enabled=_enabled("PASSKEYS_ENABLED"),
        provider=os.getenv("IDENTITY_PROVIDER_NAME"),
        redirect_uri=os.getenv("OIDC_REDIRECT_URI"),
        note="Provider metadata and credentials remain environment-scoped; no secrets are returned.",
    )


def device_policy() -> DevicePolicyResponse:
    domains = [item.strip() for item in os.getenv("ALLOWED_LOGIN_DOMAINS", "").split(",") if item.strip()]
    return DevicePolicyResponse(
        managed_device_required=_enabled("MANAGED_DEVICE_REQUIRED"),
        allowed_email_domains=domains,
        max_session_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "480")),
        admin_mfa_required=_enabled("MFA_REQUIRED_FOR_ADMIN"),
    )


def export_security_events(db: Session, limit: int) -> SecurityAuditExportResponse:
    rows = db.query(SecurityEvent).order_by(SecurityEvent.created_at.desc()).limit(min(limit, 5000)).all()
    return SecurityAuditExportResponse(
        generated_at=datetime.now(UTC),
        event_count=len(rows),
        events=[SecurityEventItem(id=row.id, user_id=row.user_id, event_type=row.event_type, outcome=row.outcome, actor_id=row.actor_id, correlation_id=row.correlation_id, metadata=row.event_metadata or {}, created_at=row.created_at) for row in rows],
        retention_note=os.getenv("SECURITY_AUDIT_RETENTION_NOTE", "Export and retain according to the approved security retention policy."),
    )
