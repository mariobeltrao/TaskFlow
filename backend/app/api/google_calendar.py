import hmac

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import admin_user
from app.core.config import get_settings
from app.db.session import SessionLocal, get_db
from app.models.google_calendar import GoogleCalendarSource
from app.models.user import User
from app.schemas.google_calendar import (
    GoogleCalendarItem,
    GoogleCalendarSourceCreate,
    GoogleCalendarSourceResponse,
    GoogleCalendarSourceUpdate,
    GoogleCalendarStatus,
    GoogleOAuthConnectResponse,
    GoogleSyncResult,
)
from app.security.tokens import create_oauth_state, decode_oauth_state
from app.services.google_calendar_service import GoogleCalendarService, GoogleOAuthService

router = APIRouter(prefix="/integrations/google-calendar", tags=["google-calendar"])


def _source_or_404(db: Session, source_id: int) -> GoogleCalendarSource:
    source = db.get(GoogleCalendarSource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fonte de calendário não encontrada")
    return source


def _sync_source_in_background(source_id: int) -> None:
    with SessionLocal() as db:
        source = db.get(GoogleCalendarSource, source_id)
        if source:
            GoogleCalendarService(db).sync_source(source)


@router.get("/status", response_model=GoogleCalendarStatus)
def integration_status(
    db: Session = Depends(get_db), _user: User = Depends(admin_user)
) -> dict[str, object]:
    service = GoogleCalendarService(db)
    connection = service.connection()
    return {
        "connected": connection is not None,
        "configured": service.configured(),
        "account_email": connection.google_account_email if connection else None,
        "last_error": connection.last_error if connection else None,
        "sources": service.list_sources() if connection else [],
    }


@router.get("/connect", response_model=GoogleOAuthConnectResponse)
def connect_google_calendar(user: User = Depends(admin_user), db: Session = Depends(get_db)):
    state = create_oauth_state(user.id)
    return {"authorization_url": GoogleOAuthService(db).authorization_url(state)}


@router.get("/callback")
def google_calendar_callback(
    code: str,
    state: str,
    user: User = Depends(admin_user),
    db: Session = Depends(get_db),
):
    if decode_oauth_state(state) != user.id:
        raise HTTPException(status_code=400, detail="Estado OAuth inválido")
    GoogleOAuthService(db).complete(code, state, user.id)
    frontend = get_settings().frontend_url.rstrip("/")
    return RedirectResponse(f"{frontend}/app?view=integrations&google=connected", status_code=303)


@router.get("/calendars", response_model=list[GoogleCalendarItem])
def list_google_calendars(
    db: Session = Depends(get_db), _user: User = Depends(admin_user)
):
    return GoogleCalendarService(db).list_calendars()


@router.post(
    "/sources", response_model=GoogleCalendarSourceResponse, status_code=status.HTTP_201_CREATED
)
def create_google_source(
    data: GoogleCalendarSourceCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(admin_user),
):
    return GoogleCalendarService(db).create_source(data)


@router.patch("/sources/{source_id}", response_model=GoogleCalendarSourceResponse)
def update_google_source(
    source_id: int,
    data: GoogleCalendarSourceUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(admin_user),
):
    return GoogleCalendarService(db).update_source(_source_or_404(db, source_id), data)


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_google_source(
    source_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(admin_user),
) -> None:
    GoogleCalendarService(db).delete_source(_source_or_404(db, source_id))


@router.post("/sync", response_model=GoogleSyncResult)
def sync_google_calendar(
    source_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _user: User = Depends(admin_user),
):
    service = GoogleCalendarService(db)
    return service.sync_source(_source_or_404(db, source_id)) if source_id else service.sync_all()


@router.post("/disconnect", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_google_calendar(
    db: Session = Depends(get_db), _user: User = Depends(admin_user)
) -> None:
    GoogleCalendarService(db).disconnect()


@router.post("/webhook", status_code=status.HTTP_204_NO_CONTENT)
def google_calendar_webhook(
    background_tasks: BackgroundTasks,
    x_goog_channel_id: str = Header(),
    x_goog_channel_token: str = Header(),
    x_goog_resource_id: str = Header(),
    db: Session = Depends(get_db),
) -> None:
    expected_token = get_settings().google_calendar_webhook_token
    if not expected_token or not hmac.compare_digest(x_goog_channel_token, expected_token):
        raise HTTPException(status_code=403, detail="Webhook inválido")
    source = db.scalar(
        select(GoogleCalendarSource).where(
            GoogleCalendarSource.channel_id == x_goog_channel_id,
            GoogleCalendarSource.enabled.is_(True),
        )
    )
    if not source or (
        source.channel_resource_id and source.channel_resource_id != x_goog_resource_id
    ):
        raise HTTPException(status_code=404, detail="Canal desconhecido")
    background_tasks.add_task(_sync_source_in_background, source.id)
