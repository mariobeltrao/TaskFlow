import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import auth, dashboard, tasks
from app.core.config import get_settings
from app.db.session import engine
from app.security.http import SecurityMiddleware, install_spa

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    poller = None
    logging.getLogger(__name__).info("TaskFlow iniciando em ambiente %s", settings.environment)
    if settings.enable_google_integration and settings.google_calendar_sync_enabled:
        from app.services.google_calendar_poller import run_google_calendar_poller

        poller = asyncio.create_task(run_google_calendar_poller())
    yield
    if poller:
        poller.cancel()
    logging.getLogger(__name__).info("TaskFlow encerrado")


production = settings.environment.lower() == "production"
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if production else "/docs",
    redoc_url=None if production else "/redoc",
    openapi_url=None if production else "/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)
app.add_middleware(SecurityMiddleware, settings=settings)
app.include_router(auth.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
if settings.enable_google_integration:
    from app.api import classroom_bridge, google_calendar

    app.include_router(google_calendar.router, prefix="/api")
    app.include_router(classroom_bridge.router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok"}


default_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
frontend_dist = (
    Path(settings.frontend_dist_dir).resolve() if settings.frontend_dist_dir else default_dist
)
install_spa(app, frontend_dist)
