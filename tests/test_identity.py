"""Enterprise identity portal, recovery, revocation, and audit tests."""

from datetime import datetime

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.schemas.identity import OnboardingInviteRequest, OnboardingVerifyRequest, RecoveryConfirmRequest, RecoveryRequest, RoleLoginRequest
from api.security.mfa import totp
from api.security.chat_auth import hash_password, verify_password
from api.services.identity_service import begin_mfa_enrollment, confirm_recovery, invite_client, request_recovery, role_login, verify_mfa_enrollment, verify_onboarding
from database.chatbot_models import AppUser
from database.config import Base
from database.identity_models import AuthSession, MfaFactor, RecoveryChallenge, SecurityEvent


class CapturingDelivery:
    def __init__(self):
        self.codes = {}

    def send(self, channel: str, destination: str, code: str) -> str:
        self.codes[channel] = code
        return "sent"


@pytest.fixture()
def db(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "identity-test-jwt-secret-longer-than-thirty-two")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add_all([
        AppUser(email="admin-identity@example.com", display_name="Admin", password_hash=hash_password("AdminPassphrase#2026"), role="platform_admin"),
        AppUser(email="client-identity@example.com", display_name="Client", password_hash=hash_password("ClientPassphrase#2026"), role="client_user", client_id=None),
    ])
    session.commit()
    yield session
    session.close(); Base.metadata.drop_all(engine)


def test_role_portals_fail_closed_on_role_mismatch(db) -> None:
    response = role_login(db, RoleLoginRequest(email="admin-identity@example.com", password="AdminPassphrase#2026", portal="admin"))
    assert response.user.role == "platform_admin"
    assert db.query(AuthSession).filter(AuthSession.user_id == response.user.id).count() == 1
    with pytest.raises(HTTPException) as mismatch:
        role_login(db, RoleLoginRequest(email="admin-identity@example.com", password="AdminPassphrase#2026", portal="client"))
    assert mismatch.value.status_code == 401


def test_recovery_is_single_use_and_revokes_sessions(db) -> None:
    login = role_login(db, RoleLoginRequest(email="admin-identity@example.com", password="AdminPassphrase#2026", portal="admin"))
    delivery = CapturingDelivery()
    request = RecoveryRequest(identifier="admin-identity@example.com", channel="email", portal="admin", correlation_id="recovery-request-001")
    request_recovery(db, request, delivery)
    challenge = db.query(RecoveryChallenge).order_by(RecoveryChallenge.created_at.desc()).first()
    assert challenge.code_hash != delivery.codes["email"]
    assert challenge.delivery_status == "sent"
    confirm = RecoveryConfirmRequest(
        identifier="admin-identity@example.com", portal="admin", code=delivery.codes["email"],
        new_password="Recovered Enterprise Passphrase 2026", correlation_id="recovery-confirm-001",
    )
    confirm_recovery(db, confirm)
    user = db.query(AppUser).filter(AppUser.email == "admin-identity@example.com").first()
    assert verify_password(confirm.new_password, user.password_hash)
    assert db.query(AuthSession).filter(AuthSession.user_id == user.id, AuthSession.revoked_at.isnot(None)).count() == 1
    assert db.query(SecurityEvent).filter(SecurityEvent.event_type == "recovery_confirm", SecurityEvent.outcome == "success").count() == 1
    with pytest.raises(HTTPException):
        confirm_recovery(db, confirm)


def test_recovery_request_is_generic_and_rate_limited(db) -> None:
    delivery = CapturingDelivery()
    payload = RecoveryRequest(identifier="missing-identity@example.com", channel="email", portal="client", correlation_id="missing-user-001")
    for _ in range(5):
        request_recovery(db, payload, delivery)
    assert delivery.codes == {}
    assert db.query(RecoveryChallenge).count() == 3
    assert db.query(SecurityEvent).filter(SecurityEvent.outcome == "rate_limited").count() == 2


def test_identity_migration_is_additive() -> None:
    migration = open("database/migrations/identity_v1.sql", encoding="utf-8").read().upper()
    for table in ["IDENTITY_PROFILES", "RECOVERY_CHALLENGES", "AUTH_SESSIONS", "SECURITY_EVENTS"]:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in migration
    assert "DROP TABLE" not in migration


def test_legacy_hardcoded_authentication_is_removed() -> None:
    active_sources = "\n".join(
        open(path, encoding="utf-8").read()
        for path in ["api/routers/admin.py", "api/routers/workbooks.py"]
    )
    for forbidden in ["admin123", "your-very-secret-key", "Admin123!", "Tenant123!", "Client123!", "demo.local"]:
        assert forbidden not in active_sources
    assert 'Depends(require_admin)' in open("api/routers/admin.py", encoding="utf-8").read()


def test_production_security_variables_are_documented() -> None:
    example = open(".env.example", encoding="utf-8").read()
    for variable in [
        "IDENTITY_TOKEN_PEPPER", "ENVIRONMENT", "CORS_ALLOWED_ORIGINS", "APP_BASE_URL",
        "ENABLE_DEMO_PROVISIONING", "ENABLE_DATABASE_RESET", "SMTP_HOST", "SMS_WEBHOOK_URL",
    ]:
        assert f"{variable}=" in example


def test_client_onboarding_requires_email_and_phone_verification(db, monkeypatch) -> None:
    monkeypatch.setenv("IDENTITY_DELIVERY_MODE", "mock")
    from database.models import Client, Portfolio

    client = Client(entity_id="ONBOARD-C1", entity_name="Onboarding Client")
    db.add(client)
    db.flush()
    portfolio = Portfolio(client_id=client.id, portfolio_code="ONBOARD-P1", portfolio_name="Onboarding Portfolio")
    db.add(portfolio)
    db.commit()
    delivery = CapturingDelivery()
    invited = invite_client(db, OnboardingInviteRequest(
        email="new-client@example.com",
        display_name="New Client",
        client_id=client.id,
        portfolio_ids=[portfolio.id],
        phone_e164="+919884455466",
    ), delivery=delivery)
    user = db.query(AppUser).filter(AppUser.id == invited.user_id).one()
    assert user.is_active is False
    assert invited.email_delivery_status == "sent"
    assert invited.sms_delivery_status == "sent"
    email_result = verify_onboarding(db, OnboardingVerifyRequest(
        user_id=user.id, channel="email", code=delivery.codes["email"], new_password="NewClientPassword#2026",
    ))
    assert email_result.active is False
    sms_result = verify_onboarding(db, OnboardingVerifyRequest(
        user_id=user.id, channel="sms", code=delivery.codes["sms"], new_password="NewClientPassword#2026",
    ))
    assert sms_result.active is True
    assert role_login(db, RoleLoginRequest(email=user.email, password="NewClientPassword#2026", portal="client")).user.id == user.id


def test_onboarding_wrong_code_does_not_activate_user(db) -> None:
    from database.models import Client

    client = Client(entity_id="ONBOARD-C2", entity_name="Wrong Code Client")
    db.add(client)
    db.commit()
    delivery = CapturingDelivery()
    invited = invite_client(db, OnboardingInviteRequest(
        email="wrong-code@example.com", display_name="Wrong Code", client_id=client.id,
    ), delivery=delivery)
    with pytest.raises(HTTPException) as error:
        verify_onboarding(db, OnboardingVerifyRequest(
            user_id=invited.user_id, channel="email", code="000000", new_password="NewClientPassword#2026",
        ))
    assert error.value.status_code == 400
    assert db.query(AppUser).filter(AppUser.id == invited.user_id, AppUser.is_active.is_(False)).count() == 1


def test_totp_mfa_enrollment_and_login(db, monkeypatch) -> None:
    monkeypatch.setenv("MFA_ENCRYPTION_KEY", "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=")
    admin = db.query(AppUser).filter(AppUser.role == "platform_admin").one()
    enrollment = begin_mfa_enrollment(db, admin)
    assert enrollment.secret not in db.query(MfaFactor).one().secret_ciphertext
    verification = verify_mfa_enrollment(db, admin, totp(enrollment.secret))
    assert verification.enabled is True
    assert len(verification.recovery_codes) == 10
    with pytest.raises(HTTPException) as missing:
        role_login(db, RoleLoginRequest(email=admin.email, password="AdminPassphrase#2026", portal="admin"))
    assert missing.value.status_code == 401
    response = role_login(db, RoleLoginRequest(email=admin.email, password="AdminPassphrase#2026", portal="admin", mfa_code=totp(enrollment.secret)))
    assert response.user.id == admin.id


def test_totp_known_vector(monkeypatch) -> None:
    monkeypatch.setenv("MFA_ENCRYPTION_KEY", "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=")
    assert totp("GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ", 59) == "287082"
