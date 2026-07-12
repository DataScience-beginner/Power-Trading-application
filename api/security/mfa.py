"""RFC 6238 TOTP helpers with encrypted factor storage."""

from base64 import b32decode, b32encode, urlsafe_b64encode
from datetime import UTC, datetime
import hashlib
import hmac
import os
import secrets
import struct
import time
from urllib.parse import quote

from cryptography.fernet import Fernet
from fastapi import HTTPException


def _fernet() -> Fernet:
    configured = os.getenv("MFA_ENCRYPTION_KEY")
    if configured:
        try:
            return Fernet(configured.encode())
        except ValueError as exc:
            raise HTTPException(status_code=503, detail="MFA encryption key is invalid") from exc
    if os.getenv("ENVIRONMENT", "development").lower() == "production":
        raise HTTPException(status_code=503, detail="MFA encryption is not configured")
    fallback = os.getenv("JWT_SECRET_KEY", "development-only-mfa-key")
    return Fernet(urlsafe_b64encode(hashlib.sha256(fallback.encode()).digest()))


def new_secret() -> str:
    """Create a 160-bit Base32 TOTP secret."""
    return b32encode(secrets.token_bytes(20)).decode().rstrip("=")


def encrypt_secret(secret: str) -> str:
    return _fernet().encrypt(secret.encode()).decode()


def decrypt_secret(ciphertext: str) -> str:
    try:
        return _fernet().decrypt(ciphertext.encode()).decode()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="MFA factor cannot be decrypted") from exc


def totp(secret: str, at_time: int | None = None) -> str:
    """Calculate a six-digit SHA-1 TOTP code for a 30-second window."""
    moment = int(time.time() if at_time is None else at_time)
    padded = secret + "=" * ((8 - len(secret) % 8) % 8)
    key = b32decode(padded, casefold=True)
    digest = hmac.new(key, struct.pack(">Q", moment // 30), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = (struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF) % 1_000_000
    return f"{value:06d}"


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    now = int(time.time())
    return any(hmac.compare_digest(totp(secret, now + offset * 30), code) for offset in range(-window, window + 1))


def provisioning_uri(secret: str, email: str) -> str:
    issuer = os.getenv("MFA_ISSUER", "Innowatt Energy AI")
    return f"otpauth://totp/{quote(issuer)}:{quote(email)}?secret={secret}&issuer={quote(issuer)}&algorithm=SHA1&digits=6&period=30"


def recovery_codes() -> tuple[list[str], list[str]]:
    plain = [f"{secrets.token_hex(4)}-{secrets.token_hex(4)}" for _ in range(10)]
    hashed = [hashlib.sha256(item.encode()).hexdigest() for item in plain]
    return plain, hashed


def consume_recovery_code(code: str, hashes: list[str]) -> tuple[bool, list[str]]:
    digest = hashlib.sha256(code.encode()).hexdigest()
    matched = any(hmac.compare_digest(digest, item) for item in hashes)
    return matched, [item for item in hashes if not hmac.compare_digest(digest, item)]


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
