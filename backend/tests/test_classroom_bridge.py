from datetime import date

from sqlalchemy import select

from app.core.config import get_settings
from app.models.enums import TaskPriority, TaskSource, TaskStatus, UserRole
from app.models.task import Task
from app.models.user import User
from tests.conftest import TestingSession

URL = "/api/integrations/classroom-bridge/import"
HEADERS = {"X-TaskFlow-Bridge-Token": "test-bridge-token"}


def payload(title: str = "Prova") -> dict[str, object]:
    return {
        "calendar_id": "calculo@example.com",
        "calendar_name": "Cálculo I",
        "subject_name": "Cálculo I",
        "professor_name": "Prof. Ada",
        "events": [
            {
                "id": "classroom-event-1",
                "title": title,
                "description": "Capítulos 1–4",
                "start": "2026-09-02T01:30:00Z",
                "end": "2026-09-02T03:00:00Z",
            }
        ],
    }


def test_incorrect_and_missing_token_are_forbidden(client):
    assert client.post(URL, json=payload()).status_code == 403
    response = client.post(URL, json=payload(), headers={"X-TaskFlow-Bridge-Token": "wrong"})
    assert response.status_code == 403


def test_correct_token_creates_task_with_admin_and_timezone_mapping(client):
    response = client.post(URL, json=payload(), headers=HEADERS)
    assert response.status_code == 200
    assert response.json() == {"created": 1, "updated": 0, "skipped": 0}

    with TestingSession() as db:
        task = db.scalar(select(Task).where(Task.source == TaskSource.CLASSROOM_BRIDGE))
        admin = db.scalar(select(User).where(User.email == "admin@test.com"))
        assert task is not None and admin is not None
        assert task.created_by == admin.id
        assert admin.role == UserRole.ADMIN
        assert task.external_id == "classroom-event-1"
        assert task.external_calendar_id == "calculo@example.com"
        assert task.due_date == date(2026, 9, 1)
        assert task.priority == TaskPriority.MEDIUM
        assert task.status == TaskStatus.PENDING


def test_reimport_updates_without_duplication(client):
    assert client.post(URL, json=payload(), headers=HEADERS).json()["created"] == 1
    response = client.post(URL, json=payload("Prova atualizada"), headers=HEADERS)
    assert response.json() == {"created": 0, "updated": 1, "skipped": 0}

    with TestingSession() as db:
        tasks = list(db.scalars(select(Task).where(Task.source == TaskSource.CLASSROOM_BRIDGE)))
        assert len(tasks) == 1
        assert tasks[0].title == "Prova atualizada"


def test_member_configured_as_bridge_admin_imports_nothing(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "classroom_bridge_admin_email", "member@test.com")
    response = client.post(URL, json=payload(), headers=HEADERS)
    assert response.status_code == 503
    with TestingSession() as db:
        assert db.scalar(select(Task)) is None


def test_manual_and_google_tasks_are_not_changed(client):
    with TestingSession() as db:
        admin = db.scalar(select(User).where(User.email == "admin@test.com"))
        common = {
            "title": "Preservar",
            "category": "Original",
            "due_date": date(2026, 1, 1),
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.COMPLETED,
            "external_id": "classroom-event-1",
            "external_calendar_id": "calculo@example.com",
            "created_by": admin.id,
        }
        manual = Task(**common, source=TaskSource.MANUAL)
        google = Task(**common, source=TaskSource.GOOGLE_CALENDAR)
        db.add_all([manual, google])
        db.commit()
        ids = (manual.id, google.id)

    assert client.post(URL, json=payload(), headers=HEADERS).status_code == 200
    with TestingSession() as db:
        manual = db.get(Task, ids[0])
        google = db.get(Task, ids[1])
        assert manual.title == "Preservar" and manual.status == TaskStatus.COMPLETED
        assert google.title == "Preservar" and google.status == TaskStatus.COMPLETED
