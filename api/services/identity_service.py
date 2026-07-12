"""Role-aware login, recovery challenges, revocation, and security auditing."""

from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import secrets
import os

from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.schemas.chatbot import TokenResponse
from api.schemas.identity import (
    OnboardingInviteRequest,
    OnboardingInviteResponse,
    OnboardingStatusResponse,
    OnboardingVerifyRequest,
    OnboardingVerifyResponse,
    MfaEnrollmentResponse,
    MfaVerifyResponse,
    RecoveryConfirmRequest,
    RecoveryRequest,
    RoleLoginRequest,
)
from api.security.chat_auth import create_access_token, hash_password, jwt_secret, verify_password
from api.services.chat_auth_service import user_response
from api.services.identity_delivery_service import IdentityDeliveryService
from database.chatbot_models import AppUser
from database.identity_models import AuthSession, IdentityProfile, MfaFactor, OnboardingChallenge, RecoveryChallenge, SecurityEvent
from api.security.mfa import decrypt_secret, encrypt_secret, new_secret, provisioning_uri, recovery_codes, utc_now as mfa_now, verify_totp, consume_recovery_code


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _digest(value: str) -> str:
    pepper = os.getenv("IDENTITY_TOKEN_PEPPER")
    if not pepper or len(pepper) < 32:
        if os.getenv("ENVIRONMENT", "development") == "production":
            raise HTTPException(status_code=503, detail="Identity recovery is not configured")
        pepper = jwt_secret()
    return hmac.new(pepper.encode(), value.encode(), hashlib.sha256).hexdigest()


def _role(portal: str) -> str:
    return "platform_admin" if portal == "admin" else "client_user"


def _event(db: Session, event_type: str, outcome: str, correlation_id: str, user: AppUser | None, actor_id: str, **metadata) -> None:
    db.add(SecurityEvent(
        user_id=user.id if user else None,
        event_type=event_type,
        outcome=outcome,
        actor_id=actor_id[:320],
        correlation_id=correlation_id,
        event_metadata=metadata,
    ))


def role_login(db: Session, payload: RoleLoginRequest) -> TokenResponse:
    """Authenticate only through the portal matching the database role."""
    user = db.query(AppUser).filter(AppUser.email == str(payload.email).lower(), AppUser.is_active.is_(True)).first()
    expected_role = _role(payload.portal)
    if not user or user.role != expected_role or not verify_password(payload.password, user.password_hash):
        _event(db, "login", "denied", f"login-{secrets.token_hex(8)}", user, str(payload.email), portal=payload.portal)
        db.commit()
        raise HTTPException(status_code=401, detail="Incorrect email, password, or portal")
    factor = db.query(MfaFactor).filter(MfaFactor.user_id == user.id, MfaFactor.enabled.is_(True)).first()
    mfa_required = user.role == "platform_admin" and os.getenv("MFA_REQUIRED_FOR_ADMIN", "false").lower() == "true"
    if factor:
        code = payload.mfa_code or ""
        secret = decrypt_secret(factor.secret_ciphertext)
        valid_totp = len(code) == 6 and code.isdigit() and verify_totp(secret, code)
        valid_recovery, remaining = consume_recovery_code(code, factor.recovery_code_hashes or [])
        if not valid_totp and not valid_recovery:
            _event(db, "mfa", "denied", f"mfa-{secrets.token_hex(8)}", user, user.email, portal=payload.portal)
            db.commit()
            raise HTTPException(status_code=401, detail="A valid MFA or recovery code is required")
        if valid_recovery:
            factor.recovery_code_hashes = remaining
        factor.last_used_at = mfa_now()
    elif mfa_required:
        _event(db, "mfa", "enrollment_required", f"mfa-{secrets.token_hex(8)}", user, user.email, portal=payload.portal)
        db.commit()
        raise HTTPException(status_code=403, detail="Administrator MFA enrollment is required")
    token, expires_at = create_access_token(user, db=db)
    _event(db, "login", "success", f"login-{secrets.token_hex(8)}", user, user.email, portal=payload.portal)
    db.commit()
    return TokenResponse(access_token=token, expires_at=expires_at, user=user_response(db, user))


def begin_mfa_enrollment(db: Session, user: AppUser) -> MfaEnrollmentResponse:
    """Create or replace a disabled encrypted TOTP factor for the current user."""
    secret = new_secret()
    factor = db.query(MfaFactor).filter(MfaFactor.user_id == user.id).first()
    if not factor:
        factor = MfaFactor(user_id=user.id, secret_ciphertext=encrypt_secret(secret), enabled=False)
        db.add(factor)
    else:
        factor.secret_ciphertext = encrypt_secret(secret)
        factor.enabled = False
        factor.recovery_code_hashes = []
        factor.verified_at = None
    db.commit()
    db.refresh(factor)
    return MfaEnrollmentResponse(factor_id=factor.id, secret=secret, provisioning_uri=provisioning_uri(secret, user.email))


def verify_mfa_enrollment(db: Session, user: AppUser, code: str) -> MfaVerifyResponse:
    """Verify one TOTP code, enable the factor, and issue one-time recovery codes."""
    factor = db.query(MfaFactor).filter(MfaFactor.user_id == user.id).first()
    if not factor or not verify_totp(decrypt_secret(factor.secret_ciphertext), code):
        raise HTTPException(status_code=400, detail="MFA verification code is invalid")
    plain, hashed = recovery_codes()
    factor.enabled = True
    factor.verified_at = mfa_now()
    factor.recovery_code_hashes = hashed
    _event(db, "mfa_enrollment", "success", f"mfa-{secrets.token_hex(8)}", user, user.email)
    db.commit()
    return MfaVerifyResponse(enabled=True, recovery_codes=plain)


def _verification_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _valid_client_scope(db: Session, client_id: int, portfolio_ids: list[int]) -> None:
    from database.models import Client, Portfolio

    if not db.query(Client.id).filter(Client.id == client_id).first():
        raise HTTPException(status_code=404, detail="Client not found")
    valid = {row.id for row in db.query(Portfolio).filter(Portfolio.id.in_(portfolio_ids), Portfolio.client_id == client_id).all()}
    if valid != set(portfolio_ids):
        raise HTTPException(status_code=400, detail="One or more portfolios are outside the client scope")


def _create_onboarding_challenge(db: Session, user: AppUser, channel: str, destination: str, delivery: IdentityDeliveryService) -> str:
    recent = db.query(OnboardingChallenge).filter(
        OnboardingChallenge.user_id == user.id,
        OnboardingChallenge.channel == channel,
        OnboardingChallenge.created_at >= _now() - timedelta(minutes=15),
    ).count()
    if recent >= 3:
        return "rate_limited"
    code = _verification_code()
    challenge = OnboardingChallenge(
        user_id=user.id,
        channel=channel,
        code_hash=_digest(code),
        expires_at=_now() + timedelta(minutes=10),
        delivery_status="pending",
    )
    db.add(challenge)
    db.flush()
    try:
        challenge.delivery_status = delivery.send(channel, destination, code)
    except Exception:
        challenge.delivery_status = "failed"
    return challenge.delivery_status


def invite_client(db: Session, payload: OnboardingInviteRequest, delivery: IdentityDeliveryService | None = None) -> OnboardingInviteResponse:
    """Create an inactive client user and send email plus optional SMS verification."""
    _valid_client_scope(db, payload.client_id, payload.portfolio_ids)
    email = str(payload.email).lower()
    if db.query(AppUser).filter(AppUser.email == email).first():
        raise HTTPException(status_code=409, detail="A user with this email already exists")
    user = AppUser(
        email=email,
        display_name=payload.display_name,
        password_hash=hash_password(secrets.token_urlsafe(32)),
        role="client_user",
        client_id=payload.client_id,
        is_active=False,
    )
    db.add(user)
    db.flush()
    from database.chatbot_models import UserPortfolioAccess
    for portfolio_id in payload.portfolio_ids:
        db.add(UserPortfolioAccess(user_id=user.id, portfolio_id=portfolio_id))
    profile = IdentityProfile(user_id=user.id, phone_e164=payload.phone_e164, must_change_password=True)
    db.add(profile)
    sender = delivery or IdentityDeliveryService()
    email_status = _create_onboarding_challenge(db, user, "email", email, sender)
    sms_status = _create_onboarding_challenge(db, user, "sms", payload.phone_e164, sender) if payload.phone_e164 else None
    _event(db, "onboarding_invite", "accepted", f"invite-{secrets.token_hex(8)}", user, email, email_status=email_status, sms_status=sms_status)
    db.commit()
    return OnboardingInviteResponse(user_id=user.id, email=user.email, email_delivery_status=email_status, sms_delivery_status=sms_status)


def verify_onboarding(db: Session, payload: OnboardingVerifyRequest) -> OnboardingVerifyResponse:
    """Verify one channel, set the first password, and activate only when required channels pass."""
    challenge = db.query(OnboardingChallenge).filter(
        OnboardingChallenge.user_id == payload.user_id,
        OnboardingChallenge.channel == payload.channel,
        OnboardingChallenge.used_at.is_(None),
    ).order_by(OnboardingChallenge.created_at.desc()).first()
    if not challenge or challenge.expires_at < _now() or challenge.attempts >= challenge.max_attempts:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    challenge.attempts += 1
    if not hmac.compare_digest(challenge.code_hash, _digest(payload.code)):
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    user = db.query(AppUser).filter(AppUser.id == payload.user_id).first()
    profile = db.query(IdentityProfile).filter(IdentityProfile.user_id == payload.user_id).first()
    if not user or not profile:
        raise HTTPException(status_code=400, detail="Invalid onboarding identity")
    challenge.used_at = _now()
    if payload.channel == "email":
        profile.email_verified = True
    else:
        profile.phone_verified = True
    user.password_hash = hash_password(payload.new_password)
    profile.password_changed_at = _now()
    profile.must_change_password = False
    user.is_active = bool(profile.email_verified and (not profile.phone_e164 or profile.phone_verified))
    _event(db, "onboarding_verify", "success", f"verify-{secrets.token_hex(8)}", user, user.email, channel=payload.channel, active=user.is_active)
    db.commit()
    return OnboardingVerifyResponse(
        user_id=user.id,
        email_verified=profile.email_verified,
        phone_verified=profile.phone_verified,
        active=user.is_active,
        message="Verification completed. You can sign in." if user.is_active else "Verification completed. Complete the remaining required channel.",
    )


def onboarding_status(db: Session, user_id: str) -> OnboardingStatusResponse:
    """Return non-secret onboarding status for an invited user."""
    user = db.query(AppUser).filter(AppUser.id == user_id).first()
    profile = db.query(IdentityProfile).filter(IdentityProfile.user_id == user_id).first() if user else None
    if not user or not profile:
        raise HTTPException(status_code=404, detail="Onboarding identity not found")
    return OnboardingStatusResponse(user_id=user.id, email_verified=profile.email_verified, phone_verified=profile.phone_verified, active=user.is_active, must_change_password=profile.must_change_password)


def request_recovery(db: Session, payload: RecoveryRequest, delivery: IdentityDeliveryService | None = None) -> None:
    """Create a rate-limited recovery challenge while preserving account enumeration resistance."""
    identifier = payload.identifier.strip().lower()
    identifier_hash = _digest(identifier)
    recent = db.query(RecoveryChallenge).filter(
        RecoveryChallenge.identifier_hash == identifier_hash,
        RecoveryChallenge.created_at >= _now() - timedelta(minutes=15),
    ).count()
    if recent >= 3:
        _event(db, "recovery_request", "rate_limited", payload.correlation_id, None, identifier, channel=payload.channel)
        db.commit()
        return
    role = _role(payload.portal)
    user = None
    destination = None
    if payload.channel == "email":
        user = db.query(AppUser).filter(AppUser.email == identifier, AppUser.role == role, AppUser.is_active.is_(True)).first()
        destination = user.email if user else None
        if user and not db.query(IdentityProfile).filter(IdentityProfile.user_id == user.id).first():
            db.add(IdentityProfile(user_id=user.id, email_verified=True))
    else:
        profile = db.query(IdentityProfile).filter(IdentityProfile.phone_e164 == identifier, IdentityProfile.phone_verified.is_(True)).first()
        user = db.query(AppUser).filter(AppUser.id == profile.user_id, AppUser.role == role, AppUser.is_active.is_(True)).first() if profile else None
        destination = profile.phone_e164 if user and profile else None
    code = f"{secrets.randbelow(1_000_000):06d}"
    challenge = RecoveryChallenge(
        user_id=user.id if user else None,
        identifier_hash=identifier_hash,
        role_scope=role,
        channel=payload.channel,
        code_hash=_digest(code),
        expires_at=_now() + timedelta(minutes=10),
    )
    db.add(challenge); db.flush()
    if destination:
        try:
            challenge.delivery_status = (delivery or IdentityDeliveryService()).send(payload.channel, destination, code)
        except Exception:
            challenge.delivery_status = "failed"
    else:
        challenge.delivery_status = "ineligible"
    _event(db, "recovery_request", "accepted", payload.correlation_id, user, identifier, channel=payload.channel, delivery_status=challenge.delivery_status)
    db.commit()


def confirm_recovery(db: Session, payload: RecoveryConfirmRequest) -> None:
    identifier = payload.identifier.strip().lower()
    challenge = db.query(RecoveryChallenge).filter(
        RecoveryChallenge.identifier_hash == _digest(identifier),
        RecoveryChallenge.role_scope == _role(payload.portal),
        RecoveryChallenge.used_at.is_(None),
    ).order_by(RecoveryChallenge.created_at.desc()).first()
    if not challenge or challenge.expires_at < _now() or challenge.attempts >= challenge.max_attempts:
        raise HTTPException(status_code=400, detail="Invalid or expired recovery code")
    challenge.attempts += 1
    if not hmac.compare_digest(challenge.code_hash, _digest(payload.code)) or not challenge.user_id:
        _event(db, "recovery_confirm", "denied", payload.correlation_id, None, identifier, attempts=challenge.attempts)
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired recovery code")
    user = db.query(AppUser).filter(AppUser.id == challenge.user_id, AppUser.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired recovery code")
    user.password_hash = hash_password(payload.new_password)
    challenge.used_at = _now()
    db.query(AuthSession).filter(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None)).update({"revoked_at": _now()})
    profile = db.query(IdentityProfile).filter(IdentityProfile.user_id == user.id).first()
    if not profile:
        profile = IdentityProfile(user_id=user.id, email_verified=challenge.channel == "email", phone_verified=challenge.channel == "sms")
        db.add(profile)
    profile.password_changed_at = _now()
    profile.must_change_password = False
    _event(db, "recovery_confirm", "success", payload.correlation_id, user, identifier, channel=challenge.channel, sessions_revoked=True)
    db.commit()
