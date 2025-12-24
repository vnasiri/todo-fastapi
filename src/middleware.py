from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


# Security Headers Middleware
class SecurityHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # CSP: Disallow unsafe-inline (except strictly needed), force HTTPS logic
        # Note: 'unsafe-inline' is often needed for Bootstrap JS if not using nonces.
        # We allow it here for simplicity with CDN, but strictly restrict sources.
        csp_policy = (
            "default-src 'self' https://cdn.jsdelivr.net;"
            "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
            "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "frame-ancestors 'self';"
        )

        response.headers["Content-Security-Policy"] = csp_policy
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )

        return response
