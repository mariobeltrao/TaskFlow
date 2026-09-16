import logging
import threading
import time
from collections import defaultdict, deque
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import Settings

logger = logging.getLogger(__name__)
MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def normalized_origin(value: str) -> str:
    parsed = urlsplit(value)
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"


class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings
        self.allowed_origins = {
            normalized_origin(origin) for origin in [settings.frontend_url, *settings.cors_origins]
        }

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        if request.method in MUTATING_METHODS and origin:
            if normalized_origin(origin) not in self.allowed_origins:
                return JSONResponse({"detail": "Origem não permitida"}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' "
            "https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; "
            "form-action 'self'"
        )
        if self.settings.environment.lower() == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class AuthRateLimiter:
    def __init__(self):
        self._attempts: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        with self._lock:
            attempts = self._attempts[key]
            while attempts and attempts[0] <= now - window_seconds:
                attempts.popleft()
            if len(attempts) >= limit:
                return False
            attempts.append(now)
            return True

    def clear(self) -> None:
        with self._lock:
            self._attempts.clear()

    def reset(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)


auth_rate_limiter = AuthRateLimiter()


def install_spa(app: FastAPI, dist_dir: Path) -> None:
    assets = dist_dir / "assets"
    favicon = dist_dir / "favicon.svg"
    index = dist_dir / "index.html"
    if not index.is_file():
        logger.info("Frontend compilado não encontrado em %s; modo API", dist_dir)
        return
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")
    if favicon.is_file():

        @app.get("/favicon.svg", include_in_schema=False)
        async def favicon_file():
            return FileResponse(favicon, media_type="image/svg+xml")

    @app.get("/{frontend_path:path}", include_in_schema=False)
    async def spa_fallback(frontend_path: str):
        if frontend_path == "api" or frontend_path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        return FileResponse(index)
