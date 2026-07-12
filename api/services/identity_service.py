"""Role-aware login, recovery challenges, revocation, and security auditing."""

from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.schemas.chatbot import TokenResponse
from api.schemas.identity import RecoveryConfirmRequest, RecoveryRequest, RoleLoginRequest
from api.security.chat_auth import create_access_token, hash_password, jwt_secret, verify_password
from api.services.chat_auth_service import user_response
from api.services.identity_delivery_service import IdentityDeliveryService
from database.chatbot_models import AppUser
from database.identity_models import AuthSession, IdentityProfile, RecoveryChallenge, SecurityEvent


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _digest(value: str) -> str:
    return hmac.new(jwt_secret().encode(), value.encode(), hashlib.sha256).hexdigest()


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
    token, expires_at = create_access_token(user, db=db)
    _event(db, "login", "success", f"login-{secrets.token_hex(8)}", user, user.email, portal=payload.portal)
    db.commit()
    return TokenResponse(access_token=token, expires_at=expires_at, user=user_response(db, user))


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
