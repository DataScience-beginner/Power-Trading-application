"""Security middleware for API headers and bounded anti-automation controls."""

from collections import defaultdict, deque
import hmac
from os import getenv
from time import monotonic, time
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from api.services.security_alert_service import emit_security_alert


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
        self._daily_requests: dict[str, tuple[int, int]] = {}

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

    def _daily_quota_exceeded(self, request: Request) -> bool:
        if request.method == "OPTIONS" or not request.url.path.startswith("/api/"):
            return False
        day = int(time() // 86_400)
        key = self._client_key(request)
        stored_day, count = self._daily_requests.get(key, (day, 0))
        if stored_day != day:
            stored_day, count = day, 0
        limit = int(getenv("API_TENANT_DAILY_QUOTA", "100000"))
        self._daily_requests[key] = (stored_day, count + 1)
        return count >= limit

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.correlation_id = correlation_id
        protected_paths = ("/api/v1/identity/", "/api/v1/auth/", "/api/upload", "/api/v1/workbooks/upload")
        if _enabled("WAF_VERIFICATION_REQUIRED", False) and request.url.path.startswith(protected_paths):
            expected = getenv("WAF_VERIFICATION_SECRET", "")
            supplied = request.headers.get("X-WAF-Verified", "")
            if not expected or not hmac.compare_digest(expected, supplied):
                await emit_security_alert("waf_verification_failed", correlation_id, self._client_key(request), request.url.path)
                response = JSONResponse(status_code=403, content={"detail": "Verified edge traffic is required."})
                response.headers["X-Request-ID"] = correlation_id
                return response
        blocked, retry_after = self._too_many_requests(request)
        if blocked:
            await emit_security_alert("rate_limit_exceeded", correlation_id, self._client_key(request), request.url.path)
            response = JSONResponse(status_code=429, content={"detail": "Too many requests. Try again later."})
            response.headers["Retry-After"] = str(retry_after)
            response.headers["X-Request-ID"] = correlation_id
            return response
        if self._daily_quota_exceeded(request):
            await emit_security_alert("daily_quota_exceeded", correlation_id, self._client_key(request), request.url.path)
            response = JSONResponse(status_code=429, content={"detail": "Daily API quota exceeded."})
            response.headers["Retry-After"] = "86400"
            response.headers["X-Request-ID"] = correlation_id
            return response

        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        # MUI/Emotion injects scoped style tags at runtime. Keep script and
        # frame restrictions strict while allowing the framework's styles.
        response.headers.setdefault("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; object-src 'none'; base-uri 'self'")
        response.headers.setdefault("X-Request-ID", correlation_id)
        if request.url.path.startswith("/api/"):
            response.headers.setdefault("Cache-Control", "no-store")
        if getenv("ENVIRONMENT", "").lower() == "production":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response
