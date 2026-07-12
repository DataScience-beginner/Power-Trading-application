"""Enterprise identity recovery, session, and security-audit persistence."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, JSON, String

from database.config import Base


def new_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class IdentityProfile(Base):
    __tablename__ = "identity_profiles"

    user_id = Column(String(36), ForeignKey("app_users.id"), primary_key=True)
    phone_e164 = Column(String(20), nullable=True, unique=True)
    email_verified = Column(Boolean, nullable=False, default=False)
    phone_verified = Column(Boolean, nullable=False, default=False)
    must_change_password = Column(Boolean, nullable=False, default=False)
    password_changed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)


class RecoveryChallenge(Base):
    __tablename__ = "recovery_challenges"
    __table_args__ = (Index("ix_recovery_lookup", "identifier_hash", "created_at"),)

    id = Column(String(36), primary_key=True, default=new_id)
    user_id = Column(String(36), ForeignKey("app_users.id"), nullable=True, index=True)
    identifier_hash = Column(String(64), nullable=False, index=True)
    role_scope = Column(String(30), nullable=False)
    channel = Column(String(20), nullable=False)
    code_hash = Column(String(64), nullable=False)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=5)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    delivery_status = Column(String(30), nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, default=utc_now)


class OnboardingChallenge(Base):
    """Single-use email or SMS verification challenge for invited users."""

    __tablename__ = "onboarding_challenges"
    __table_args__ = (Index("ix_onboarding_lookup", "user_id", "channel", "created_at"),)

    id = Column(String(36), primary_key=True, default=new_id)
    user_id = Column(String(36), ForeignKey("app_users.id"), nullable=False, index=True)
    channel = Column(String(20), nullable=False)
    code_hash = Column(String(64), nullable=False)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=5)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    delivery_status = Column(String(30), nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, default=utc_now)


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("app_users.id"), nullable=False, index=True)
    role = Column(String(30), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)


class SecurityEvent(Base):
    __tablename__ = "security_events"
    __table_args__ = (Index("ix_security_event_subject", "user_id", "created_at"),)

    id = Column(String(36), primary_key=True, default=new_id)
    user_id = Column(String(36), ForeignKey("app_users.id"), nullable=True, index=True)
    event_type = Column(String(80), nullable=False, index=True)
    outcome = Column(String(30), nullable=False)
    actor_type = Column(String(30), nullable=False, default="user")
    actor_id = Column(String(320), nullable=True)
    correlation_id = Column(String(100), nullable=False, index=True)
    event_metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=utc_now)
