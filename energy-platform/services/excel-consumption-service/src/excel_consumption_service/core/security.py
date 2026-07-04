import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from pydantic import BaseModel

from excel_consumption_service.core.config import get_settings


class TokenPayload(BaseModel):
    """The small token payload used by the current auth flow."""

    sub: str
    exp: int


def hash_password(password: str) -> str:
    """Store passwords with PBKDF2 so plaintext credentials never touch the database."""

    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"{base64.b64encode(salt).decode()}:{base64.b64encode(digest).decode()}"


def verify_password(password: str, stored_value: str) -> bool:
    """Verify password hashes using constant-time comparison."""

    salt_b64, digest_b64 = stored_value.split(":")
    salt = base64.b64decode(salt_b64.encode())
    expected_digest = base64.b64decode(digest_b64.encode())
    candidate_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        120_000,
    )
    return hmac.compare_digest(candidate_digest, expected_digest)


def create_access_token(subject: str) -> str:
    """Issue a signed JWT token for the authenticated user."""

    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": subject, "exp": expires_at},
        settings.jwt_secret,
        algorithm="HS256",
    )


def decode_access_token(token: str) -> TokenPayload:
    """Validate and decode the current JWT token."""

    settings = get_settings()
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    return TokenPayload.model_validate(payload)
