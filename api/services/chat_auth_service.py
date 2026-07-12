"""Database-backed SaaS user onboarding and authentication services."""

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.schemas.chatbot import AdminRecoveryRequest, PasswordChangeRequest, UserCreateRequest, UserResponse, BootstrapAdminRequest
from api.security.chat_auth import hash_password, verify_password
from database.chatbot_models import AppUser, UserPortfolioAccess
from database.models import Client, Portfolio


def portfolio_ids(db: Session, user_id: str) -> list[int]:
    return [row.portfolio_id for row in db.query(UserPortfolioAccess).filter(UserPortfolioAccess.user_id == user_id).all()]


def user_response(db: Session, user: AppUser) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        client_id=user.client_id,
        portfolio_ids=portfolio_ids(db, user.id),
    )


def bootstrap_admin(db: Session, payload: BootstrapAdminRequest) -> AppUser:
    """Create the first administrator only; later users require admin JWT."""
    if db.query(AppUser).filter(AppUser.role == "platform_admin").first():
        raise HTTPException(status_code=409, detail="A platform administrator already exists")
    user = AppUser(
        email=str(payload.email).lower(),
        display_name=payload.display_name,
        password_hash=hash_password(payload.password),
        role="platform_admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_user(db: Session, payload: UserCreateRequest) -> AppUser:
    """Create a role-scoped user and validate all client/portfolio membership."""
    if payload.client_id and not db.query(Client.id).filter(Client.id == payload.client_id).first():
        raise HTTPException(status_code=404, detail="Client not found")
    if payload.portfolio_ids:
        valid = {
            row.id
            for row in db.query(Portfolio).filter(
                Portfolio.id.in_(payload.portfolio_ids),
                Portfolio.client_id == payload.client_id,
            ).all()
        }
        if valid != set(payload.portfolio_ids):
            raise HTTPException(status_code=400, detail="One or more portfolios are outside the client scope")
    user = AppUser(
        email=str(payload.email).lower(),
        display_name=payload.display_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
        client_id=payload.client_id,
    )
    try:
        db.add(user)
        db.flush()
        for portfolio_id in payload.portfolio_ids:
            db.add(UserPortfolioAccess(user_id=user.id, portfolio_id=portfolio_id))
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="A user with this email already exists") from exc


def authenticate(db: Session, email: str, password: str) -> AppUser:
    """Authenticate an active user with a generic failure response."""
    user = db.query(AppUser).filter(AppUser.email == email.lower(), AppUser.is_active.is_(True)).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return user


def change_password(db: Session, user: AppUser, payload: PasswordChangeRequest) -> None:
    """Change an authenticated user's password after verifying the current secret."""
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    if verify_password(payload.new_password, user.password_hash):
        raise HTTPException(status_code=400, detail="New password must be different from the current password")
    user.password_hash = hash_password(payload.new_password)
    from database.identity_models import AuthSession
    from datetime import UTC, datetime
    db.query(AuthSession).filter(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None)).update(
        {"revoked_at": datetime.now(UTC).replace(tzinfo=None)}
    )
    db.commit()


def recover_platform_admin(db: Session, payload: AdminRecoveryRequest) -> None:
    """Reset only an active platform administrator after service-key authorization."""
    user = db.query(AppUser).filter(
        AppUser.email == str(payload.email).lower(),
        AppUser.role == "platform_admin",
        AppUser.is_active.is_(True),
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Active platform administrator not found")
    user.password_hash = hash_password(payload.new_password)
    from database.identity_models import AuthSession
    from datetime import UTC, datetime
    db.query(AuthSession).filter(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None)).update(
        {"revoked_at": datetime.now(UTC).replace(tzinfo=None)}
    )
    db.commit()
