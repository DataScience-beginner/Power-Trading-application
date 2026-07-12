"""Typed security posture, enterprise identity, and audit-export contracts."""

from datetime import datetime
from pydantic import BaseModel, Field


class ControlStatus(BaseModel):
    control: str
    status: str
    evidence: str
    activation_dependency: str | None = None


class SecurityPostureResponse(BaseModel):
    environment: str
    controls: list[ControlStatus]
    production_ready: bool


class EnterpriseIdentityStatus(BaseModel):
    oidc_configured: bool
    saml_configured: bool
    scim_configured: bool
    passkeys_enabled: bool
    provider: str | None
    redirect_uri: str | None
    note: str


class SecurityEventItem(BaseModel):
    id: str
    user_id: str | None
    event_type: str
    outcome: str
    actor_id: str | None
    correlation_id: str
    metadata: dict
    created_at: datetime


class SecurityAuditExportResponse(BaseModel):
    generated_at: datetime
    event_count: int
    events: list[SecurityEventItem]
    retention_note: str


class DevicePolicyResponse(BaseModel):
    managed_device_required: bool
    allowed_email_domains: list[str] = Field(default_factory=list)
    max_session_minutes: int
    admin_mfa_required: bool
