import asyncio
import logging

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services.google_calendar_service import GoogleCalendarService

logger = logging.getLogger(__name__)


def sync_enabled_sources() -> None:
    with SessionLocal() as db:
        try:
            GoogleCalendarService(db).sync_all()
        except Exception:
            logger.exception("Falha na sincronização periódica do Google Calendar")


async def run_google_calendar_poller() -> None:
    settings = get_settings()
    interval = max(1, settings.google_calendar_sync_interval_minutes) * 60
    while True:
        await asyncio.sleep(interval)
        await asyncio.to_thread(sync_enabled_sources)
