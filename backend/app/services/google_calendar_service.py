import logging
import os
import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any, Protocol
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.enums import TaskPriority, TaskSource, TaskStatus
from app.models.google_calendar import GoogleCalendarConnection, GoogleCalendarSource
from app.models.task import Task
from app.schemas.google_calendar import GoogleCalendarSourceCreate, GoogleCalendarSourceUpdate
from app.security.google_tokens import decrypt_google_token, encrypt_google_token

logger = logging.getLogger(__name__)
GOOGLE_CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar.readonly"


class SyncTokenExpired(Exception):
    pass


class CalendarGateway(Protocol):
    def list_calendars(self) -> list[dict[str, Any]]: ...

    def list_events(
        self, calendar_id: str, sync_token: str | None
    ) -> tuple[list[dict[str, Any]], str]: ...

    def watch_events(
        self, calendar_id: str, address: str, token: str, channel_id: str
    ) -> dict[str, Any]: ...

    def stop_channel(self, channel_id: str, resource_id: str) -> None: ...


class GoogleCalendarGateway:
    def __init__(self, refresh_token: str, settings: Settings | None = None):
        self.settings = settings or get_settings()
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.settings.google_client_id,
            client_secret=self.settings.google_client_secret,
            scopes=[GOOGLE_CALENDAR_SCOPE],
        )
        self.client = build("calendar", "v3", credentials=credentials, cache_discovery=False)

    def list_calendars(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page_token = None
        while True:
            response = self.client.calendarList().list(pageToken=page_token).execute()
            items.extend(response.get("items", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                return items

    def list_events(
        self, calendar_id: str, sync_token: str | None
    ) -> tuple[list[dict[str, Any]], str]:
        items: list[dict[str, Any]] = []
        page_token = None
        while True:
            params: dict[str, Any] = {
                "calendarId": calendar_id,
                "showDeleted": True,
                "singleEvents": True,
                "pageToken": page_token,
            }
            if sync_token:
                params["syncToken"] = sync_token
            else:
                params["timeMin"] = (datetime.now(UTC) - timedelta(days=30)).isoformat()
            try:
                response = self.client.events().list(**params).execute()
            except HttpError as exc:
                if exc.resp.status == 410:
                    raise SyncTokenExpired from exc
                raise
            items.extend(response.get("items", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                next_sync_token = response.get("nextSyncToken")
                if not next_sync_token:
                    raise RuntimeError("Google não retornou nextSyncToken")
                return items, next_sync_token

    def watch_events(
        self, calendar_id: str, address: str, token: str, channel_id: str
    ) -> dict[str, Any]:
        body = {"id": channel_id, "type": "web_hook", "address": address, "token": token}
        return self.client.events().watch(calendarId=calendar_id, body=body).execute()

    def stop_channel(self, channel_id: str, resource_id: str) -> None:
        self.client.channels().stop(body={"id": channel_id, "resourceId": resource_id}).execute()


class GoogleOAuthService:
    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()

    def _ensure_configured(self) -> None:
        required = (
            self.settings.google_client_id,
            self.settings.google_client_secret,
            self.settings.google_redirect_uri,
            self.settings.google_token_encryption_key,
        )
        if not all(required):
            raise HTTPException(status_code=503, detail="Integração Google não configurada")

    def _flow(self, state: str | None = None) -> Flow:
        self._ensure_configured()
        redirect_host = urlparse(self.settings.google_redirect_uri).hostname
        is_local_development = (
            self.settings.environment == "development"
            and redirect_host in {"localhost", "127.0.0.1"}
        )
        if is_local_development:
            os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.settings.google_client_id,
                    "client_secret": self.settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.settings.google_redirect_uri],
                }
            },
            scopes=[GOOGLE_CALENDAR_SCOPE],
            state=state,
        )
        flow.redirect_uri = self.settings.google_redirect_uri
        return flow

    def authorization_url(self, state: str) -> str:
        url, _ = self._flow(state).authorization_url(
            access_type="offline", prompt="consent", include_granted_scopes="true"
        )
        return url

    def complete(self, code: str, state: str, user_id: int) -> GoogleCalendarConnection:
        flow = self._flow(state)
        flow.fetch_token(code=code)
        credentials = flow.credentials
        existing = self.db.scalar(select(GoogleCalendarConnection).limit(1))
        refresh_token = credentials.refresh_token
        if not refresh_token and existing:
            refresh_token = decrypt_google_token(existing.encrypted_refresh_token)
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Google não forneceu acesso offline")
        client = build("calendar", "v3", credentials=credentials, cache_discovery=False)
        calendars = client.calendarList().list().execute().get("items", [])
        primary = next((item for item in calendars if item.get("primary")), None)
        account_email = (primary or (calendars[0] if calendars else {})).get("id", "Conta Google")
        if existing:
            existing.google_account_email = account_email
            existing.encrypted_refresh_token = encrypt_google_token(refresh_token)
            existing.created_by = user_id
            existing.last_error = None
            connection = existing
        else:
            connection = GoogleCalendarConnection(
                google_account_email=account_email,
                encrypted_refresh_token=encrypt_google_token(refresh_token),
                created_by=user_id,
            )
            self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection


def _parse_updated(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def normalize_google_event(
    event: dict[str, Any], source: GoogleCalendarSource, app_timezone: str
) -> dict[str, Any] | None:
    title = event.get("summary")
    start = event.get("start") or {}
    if not isinstance(title, str) or not title.strip() or not isinstance(start, dict):
        return None
    due_date: date | None = None
    if isinstance(start.get("date"), str):
        due_date = date.fromisoformat(start["date"])
    elif isinstance(start.get("dateTime"), str):
        event_datetime = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
        event_zone = start.get("timeZone") if isinstance(start.get("timeZone"), str) else None
        zone = ZoneInfo(event_zone or app_timezone)
        if event_datetime.tzinfo is None:
            event_datetime = event_datetime.replace(tzinfo=zone)
        due_date = event_datetime.astimezone(zone).date()
    if not due_date:
        return None
    organizer = event.get("organizer") or {}
    organizer_name = None
    if isinstance(organizer, dict):
        organizer_name = organizer.get("displayName") or organizer.get("email")
    return {
        "title": title.strip(),
        "description": (
            event.get("description") if isinstance(event.get("description"), str) else None
        ),
        "category": source.subject_name,
        "responsible": source.professor_name or organizer_name,
        "due_date": due_date,
        "external_updated_at": _parse_updated(event.get("updated")),
    }


class GoogleCalendarService:
    def __init__(
        self,
        db: Session,
        gateway: CalendarGateway | None = None,
        settings: Settings | None = None,
    ):
        self.db = db
        self.settings = settings or get_settings()
        self._injected_gateway = gateway

    def connection(self) -> GoogleCalendarConnection | None:
        return self.db.scalar(select(GoogleCalendarConnection).limit(1))

    def configured(self) -> bool:
        return bool(
            self.settings.google_client_id
            and self.settings.google_client_secret
            and self.settings.google_token_encryption_key
        )

    def gateway(self) -> CalendarGateway:
        if self._injected_gateway:
            return self._injected_gateway
        connection = self.connection()
        if not connection:
            raise HTTPException(status_code=409, detail="Google Calendar não conectado")
        return GoogleCalendarGateway(
            decrypt_google_token(connection.encrypted_refresh_token), self.settings
        )

    def list_calendars(self) -> list[dict[str, object]]:
        return [
            {
                "id": item["id"],
                "name": item.get("summary", item["id"]),
                "primary": item.get("primary", False),
            }
            for item in self.gateway().list_calendars()
            if item.get("id")
        ]

    def list_sources(self) -> list[GoogleCalendarSource]:
        return list(self.db.scalars(select(GoogleCalendarSource).order_by(GoogleCalendarSource.id)))

    def create_source(self, data: GoogleCalendarSourceCreate) -> GoogleCalendarSource:
        connection = self.connection()
        if not connection:
            raise HTTPException(status_code=409, detail="Google Calendar não conectado")
        calendars = {item["id"]: item for item in self.list_calendars()}
        selected = calendars.get(data.calendar_id)
        if not selected:
            raise HTTPException(status_code=400, detail="Calendário não disponível nesta conta")
        source = GoogleCalendarSource(
            connection_id=connection.id,
            calendar_id=data.calendar_id,
            calendar_name=str(selected["name"]),
            subject_name=data.subject_name,
            professor_name=data.professor_name,
            enabled=data.enabled,
        )
        self.db.add(source)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(status_code=409, detail="Calendário já selecionado") from exc
        self.db.refresh(source)
        if source.enabled:
            self.register_watch(source)
        return source

    def update_source(
        self, source: GoogleCalendarSource, data: GoogleCalendarSourceUpdate
    ) -> GoogleCalendarSource:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(source, field, value)
        self.db.commit()
        self.db.refresh(source)
        if source.enabled and not source.channel_id:
            self.register_watch(source)
        return source

    def delete_source(self, source: GoogleCalendarSource) -> None:
        self._stop_watch(source)
        self.db.delete(source)
        self.db.commit()

    def register_watch(self, source: GoogleCalendarSource) -> None:
        url = self.settings.google_calendar_webhook_url
        token = self.settings.google_calendar_webhook_token
        if not url or not url.startswith("https://") or not token:
            return
        source.channel_id = str(uuid.uuid4())
        self.db.commit()
        try:
            result = self.gateway().watch_events(
                source.calendar_id, url, token, source.channel_id
            )
        except Exception:
            source.channel_id = None
            self.db.commit()
            raise
        source.channel_resource_id = result.get("resourceId")
        expiration = result.get("expiration")
        source.channel_expires_at = (
            datetime.fromtimestamp(int(expiration) / 1000, UTC) if expiration else None
        )
        self.db.commit()

    def _stop_watch(self, source: GoogleCalendarSource) -> None:
        if not source.channel_id or not source.channel_resource_id:
            return
        try:
            self.gateway().stop_channel(source.channel_id, source.channel_resource_id)
        except Exception:
            logger.warning("Não foi possível encerrar o canal Google", exc_info=True)

    def sync_source(self, source: GoogleCalendarSource) -> dict[str, int]:
        counts = {"created": 0, "updated": 0, "deleted": 0, "skipped": 0}
        if not source.enabled:
            return counts
        gateway = self.gateway()
        try:
            try:
                events, next_sync_token = gateway.list_events(source.calendar_id, source.sync_token)
            except SyncTokenExpired:
                self.db.execute(
                    delete(Task).where(
                        Task.source == TaskSource.GOOGLE_CALENDAR,
                        Task.external_calendar_id == source.calendar_id,
                    )
                )
                source.sync_token = None
                self.db.flush()
                events, next_sync_token = gateway.list_events(source.calendar_id, None)
            for event in events:
                external_id = event.get("id")
                if not isinstance(external_id, str) or not external_id:
                    counts["skipped"] += 1
                    continue
                task = self.db.scalar(
                    select(Task).where(
                        Task.source == TaskSource.GOOGLE_CALENDAR,
                        Task.external_calendar_id == source.calendar_id,
                        Task.external_id == external_id,
                    )
                )
                if event.get("status") == "cancelled":
                    if task:
                        self.db.delete(task)
                        counts["deleted"] += 1
                    else:
                        counts["skipped"] += 1
                    continue
                normalized = normalize_google_event(event, source, self.settings.app_timezone)
                if not normalized:
                    counts["skipped"] += 1
                    logger.info("Evento Google ignorado por ausência de título ou data")
                    continue
                if task:
                    for field, value in normalized.items():
                        setattr(task, field, value)
                    counts["updated"] += 1
                else:
                    connection = self.connection()
                    if not connection:
                        raise RuntimeError("Conexão Google ausente")
                    self.db.add(
                        Task(
                            **normalized,
                            priority=TaskPriority.MEDIUM,
                            status=TaskStatus.PENDING,
                            source=TaskSource.GOOGLE_CALENDAR,
                            external_id=external_id,
                            external_calendar_id=source.calendar_id,
                            created_by=connection.created_by,
                        )
                    )
                    counts["created"] += 1
            source.sync_token = next_sync_token
            source.last_synced_at = datetime.now(UTC)
            source.last_error = None
            self.db.commit()
            return counts
        except Exception as exc:
            self.db.rollback()
            source = self.db.get(GoogleCalendarSource, source.id)
            if source:
                source.last_error = str(exc)[:500]
                self.db.commit()
            raise

    def sync_all(self) -> dict[str, int]:
        total = {"created": 0, "updated": 0, "deleted": 0, "skipped": 0}
        for source in self.db.scalars(
            select(GoogleCalendarSource).where(GoogleCalendarSource.enabled.is_(True))
        ):
            result = self.sync_source(source)
            for key, value in result.items():
                total[key] += value
        return total

    def disconnect(self) -> None:
        connection = self.connection()
        if not connection:
            return
        for source in list(connection.sources):
            self._stop_watch(source)
        self.db.delete(connection)
        self.db.commit()
