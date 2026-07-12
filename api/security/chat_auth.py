"""JWT authentication, password hashing, and tenant-scope authorization."""

from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database.chatbot_models import AppUser, UserPortfolioAccess
from database.config import get_db
from database.models import Portfolio


ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str) -> str:
    """Hash a password with PBKDF2-SHA256 and a random salt."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"pbkdf2_sha256$310000${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    """Verify a password without timing-sensitive string comparison."""
    try:
        algorithm, rounds, salt_hex, expected_hex = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds))
        return hmac.compare_digest(digest.hex(), expected_hex)
    except (ValueError, TypeError):
        return False


def jwt_secret() -> str:
    """Return configured JWT secret or fail closed."""
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret or len(secret) < 32:
        raise HTTPException(status_code=503, detail="JWT authentication is disabled until JWT_SECRET_KEY is configured")
    return secret


def create_access_token(user: AppUser, db: Session | None = None) -> tuple[str, datetime]:
    """Create a signed token containing identity and role, not trusted scope input."""
    expires_at = datetime.now(UTC) + timedelta(minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "480")))
    session_id = secrets.token_hex(18)
    payload = {"sub": user.id, "role": user.role, "jti": session_id, "exp": expires_at}
    if db is not None:
        from database.identity_models import AuthSession
        db.add(AuthSession(id=session_id, user_id=user.id, role=user.role, expires_at=expires_at.replace(tzinfo=None)))
        db.flush()
    return jwt.encode(payload, jwt_secret(), algorithm=ALGORITHM), expires_at


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> AppUser:
    """Resolve an active user from a signed token and current database state."""
    error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")
    try:
        payload = jwt.decode(token, jwt_secret(), algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        session_id = payload.get("jti")
        if not user_id:
            raise error
    except JWTError as exc:
        raise error from exc
    user = db.query(AppUser).filter(AppUser.id == user_id, AppUser.is_active.is_(True)).first()
    if not user:
        raise error
    if session_id:
        from database.identity_models import AuthSession
        session = db.query(AuthSession).filter(AuthSession.id == session_id, AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None)).first()
        if not session:
            raise error
    return user


def require_admin(user: AppUser = Depends(get_current_user)) -> AppUser:
    """Require an active platform-admin identity."""
    if user.role != "platform_admin":
        raise HTTPException(status_code=403, detail="Platform administrator role required")
    return user


def authorize_scope(db: Session, user: AppUser, client_id: int, portfolio_id: int | None) -> None:
    """Authorize client/portfolio scope from database membership, never user text."""
    if user.role != "platform_admin" and user.client_id != client_id:
        raise HTTPException(status_code=403, detail="Client scope is not authorized")
    if portfolio_id is None:
        return
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.client_id == client_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio is not within the client scope")
    if user.role != "platform_admin":
        restrictions = db.query(UserPortfolioAccess).filter(UserPortfolioAccess.user_id == user.id).all()
        if restrictions and portfolio_id not in {item.portfolio_id for item in restrictions}:
            raise HTTPException(status_code=403, detail="Portfolio scope is not authorized")
