from datetime import datetime

from sqlalchemy import select

from app.core.config import get_settings
from app.models.enums import TaskPriority, TaskSource, TaskStatus
from app.models.google_calendar import GoogleCalendarConnection, GoogleCalendarSource
from app.models.task import Task
from app.models.user import User
from app.services.google_calendar_service import (
    GoogleCalendarService,
    SyncTokenExpired,
    normalize_google_event,
)
from tests.conftest import TestingSession, login


class FakeGateway:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def list_calendars(self):
        return [{"id": "class@example.com", "summary": "Class", "primary": False}]

    def list_events(self, calendar_id, sync_token):
        self.calls.append((calendar_id, sync_token))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def watch_events(self, calendar_id, address, token, channel_id):
        return {}

    def stop_channel(self, channel_id, resource_id):
        return None


def integration_records():
    with TestingSession() as db:
        admin = db.scalar(select(User).where(User.email == "admin@test.com"))
        connection = GoogleCalendarConnection(
            google_account_email="owner@example.com",
            encrypted_refresh_token="not-used-by-fake",
            created_by=admin.id,
        )
        db.add(connection)
        db.flush()
        source = GoogleCalendarSource(
            connection_id=connection.id,
            calendar_id="class@example.com",
            calendar_name="Class",
            subject_name="Cálculo I",
            professor_name="Professor X",
            enabled=True,
        )
        db.add(source)
        db.commit()
        return source.id


def event(title="Exam", updated="2026-08-31T10:00:00Z", status="confirmed"):
    return {
        "id": "google-event-1",
        "status": status,
        "summary": title,
        "description": "Chapter 4",
        "start": {"dateTime": "2026-09-02T23:30:00-03:00", "timeZone": "America/Fortaleza"},
        "updated": updated,
        "organizer": {"displayName": "Ignored because source has professor"},
    }


def test_event_conversion_respects_mapping_and_timezone(client):
    source_id = integration_records()
    with TestingSession() as db:
        source = db.get(GoogleCalendarSource, source_id)
        normalized = normalize_google_event(event(), source, "America/Fortaleza")
        assert normalized["title"] == "Exam"
        assert normalized["category"] == "Cálculo I"
        assert normalized["responsible"] == "Professor X"
        assert normalized["due_date"].isoformat() == "2026-09-02"


def test_initial_sync_is_idempotent_and_updates_existing_event(client):
    source_id = integration_records()
    gateway = FakeGateway([([event()], "sync-1"), ([event("Updated exam")], "sync-2")])
    with TestingSession() as db:
        service = GoogleCalendarService(db, gateway=gateway, settings=get_settings())
        source = db.get(GoogleCalendarSource, source_id)
        first = service.sync_source(source)
        assert first["created"] == 1
        assert source.sync_token == "sync-1"
        second = service.sync_source(source)
        assert second["created"] == 0 and second["updated"] == 1
        task = db.scalar(select(Task).where(Task.external_id == "google-event-1"))
        assert task.title == "Updated exam"
        assert task.source == TaskSource.GOOGLE_CALENDAR
        assert source.sync_token == "sync-2"
        assert db.query(Task).filter(Task.external_id == "google-event-1").count() == 1


def test_cancelled_event_removes_only_imported_task(client):
    source_id = integration_records()
    gateway = FakeGateway([([event()], "sync-1"), ([event(status="cancelled")], "sync-2")])
    with TestingSession() as db:
        admin = db.scalar(select(User).where(User.email == "admin@test.com"))
        manual = Task(
            title="Exam",
            category="Manual",
            due_date=datetime(2026, 9, 2).date(),
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            created_by=admin.id,
        )
        db.add(manual)
        db.commit()
        service = GoogleCalendarService(db, gateway=gateway, settings=get_settings())
        source = db.get(GoogleCalendarSource, source_id)
        service.sync_source(source)
        result = service.sync_source(source)
        assert result["deleted"] == 1
        assert db.get(Task, manual.id) is not None
        assert db.scalar(select(Task).where(Task.source == TaskSource.GOOGLE_CALENDAR)) is None


def test_expired_sync_token_forces_full_sync_and_replaces_token(client):
    source_id = integration_records()
    gateway = FakeGateway([SyncTokenExpired(), ([event("Fresh")], "fresh-token")])
    with TestingSession() as db:
        source = db.get(GoogleCalendarSource, source_id)
        source.sync_token = "expired-token"
        db.commit()
        service = GoogleCalendarService(db, gateway=gateway, settings=get_settings())
        result = service.sync_source(source)
        assert result["created"] == 1
        assert gateway.calls == [
            ("class@example.com", "expired-token"),
            ("class@example.com", None),
        ]
        assert source.sync_token == "fresh-token"


def test_webhook_validation_and_member_admin_boundary(client):
    login(client, "member@test.com")
    for path in (
        "/api/integrations/google-calendar/status",
        "/api/integrations/google-calendar/calendars",
    ):
        assert client.get(path).status_code == 403
    assert client.post("/api/integrations/google-calendar/sync").status_code == 403
    assert client.post(
        "/api/integrations/google-calendar/webhook",
        headers={
            "X-Goog-Channel-Id": "unknown",
            "X-Goog-Channel-Token": "wrong",
            "X-Goog-Resource-Id": "unknown",
        },
    ).status_code == 403
