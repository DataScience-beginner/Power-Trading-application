from collections.abc import Iterable

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from excel_consumption_service.db.session import get_db
from excel_consumption_service.schemas.auth import AuthenticatedUser
from excel_consumption_service.services.authentication import decode_access_token, get_authenticated_user


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    """Resolve the current user from the bearer token."""

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )

    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_access_token(token)
    return get_authenticated_user(db=db, user_id=payload.sub)


def require_roles(*role_codes: str):
    """Return a dependency that enforces any-of role membership."""

    required_codes = set(role_codes)

    def dependency(
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if not required_codes.intersection(current_user.role_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have the required role.",
            )
        return current_user

    return dependency


def has_role(current_user: AuthenticatedUser, allowed: Iterable[str]) -> bool:
    """Small helper for route-level checks when full dependency wrappers are unnecessary."""

    return bool(set(allowed).intersection(current_user.role_codes))
