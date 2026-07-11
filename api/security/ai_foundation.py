"""Fail-closed service authentication for AI foundation data capabilities."""

import hmac
import os

from fastapi import Header, HTTPException, status


def require_ai_foundation_access(
    x_ai_foundation_key: str | None = Header(None, description="Service credential for governed AI foundation operations."),
) -> str:
    """Require a configured service key; deny access when configuration is absent."""
    expected = os.getenv("AI_FOUNDATION_API_KEY")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI foundation protected operations are disabled until AI_FOUNDATION_API_KEY is configured",
        )
    if not x_ai_foundation_key or not hmac.compare_digest(x_ai_foundation_key, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid AI foundation service credential")
    return "service-authenticated"
