"""Security middleware for API headers and bounded anti-automation controls."""

from collections import defaultdict, deque
from os import getenv
from time import monotonic

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware


def _enabled(name: str, default: bool = True) -> bool:
    return getenv(name, str(default).lower()).lower() == "true"


class ApiSecurityMiddleware(BaseHTTPMiddleware):
    """Apply safe headers and a bounded in-process rate limit.

    The memory limiter is a baseline for one-instance deployments. Multi-instance
    production should use a shared Redis/API-gateway limiter before scaling out.
    """

    def __init__(self, app):
        super().__init__(app)
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    @staticmethod
    def _client_key(request: Request) -> str:
        return request.client.host if request.client else "unknown"

    @staticmethod
    def _limit_for(path: str) -> tuple[int, int]:
        if path.startswith("/api/v1/identity/") or path.startswith("/api/v1/auth/"):
            return int(getenv("AUTH_RATE_LIMIT_PER_MINUTE", "20")), 60
        if path.startswith("/api/upload") or path.startswith("/api/v1/workbooks/upload"):
            return int(getenv("UPLOAD_RATE_LIMIT_PER_MINUTE", "20")), 60
        return int(getenv("API_RATE_LIMIT_PER_MINUTE", "120")), 60

    def _too_many_requests(self, request: Request) -> tuple[bool, int]:
        if not _enabled("RATE_LIMIT_ENABLED", True) or request.method == "OPTIONS":
            return False, 0
        path = request.url.path
        if not path.startswith("/api/"):
            return False, 0
        limit, window = self._limit_for(path)
        now = monotonic()
        key = f"{self._client_key(request)}:{path}"
        bucket = self._requests[key]
        while bucket and now - bucket[0] >= window:
            bucket.popleft()
        if len(bucket) >= limit:
            retry_after = max(1, int(window - (now - bucket[0])))
            return True, retry_after
        bucket.append(now)
        if len(self._requests) > 10_000:
            self._requests = defaultdict(deque, {
                item_key: item_bucket
                for item_key, item_bucket in self._requests.items()
                if item_bucket and now - item_bucket[-1] < window
            })
        return False, 0

    async def dispatch(self, request: Request, call_next) -> Response:
        blocked, retry_after = self._too_many_requests(request)
        if blocked:
            response = JSONResponse(status_code=429, content={"detail": "Too many requests. Try again later."})
            response.headers["Retry-After"] = str(retry_after)
            return response

        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if request.url.path.startswith("/api/"):
            response.headers.setdefault("Cache-Control", "no-store")
        if getenv("ENVIRONMENT", "").lower() == "production":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response
