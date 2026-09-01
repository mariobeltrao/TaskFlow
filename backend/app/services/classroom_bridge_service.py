from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.enums import TaskPriority, TaskSource, TaskStatus, UserRole
from app.models.task import Task
from app.models.user import User
from app.schemas.classroom_bridge import ClassroomBridgeImport


class ClassroomBridgeService:
    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()

    def _admin(self) -> User:
        email = self.settings.classroom_bridge_admin_email.strip()
        if not email:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="CLASSROOM_BRIDGE_ADMIN_EMAIL não configurado",
            )
        user = self.db.scalar(select(User).where(func.lower(User.email) == email.lower()))
        if not user or user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Administrador da Classroom Bridge inválido",
            )
        return user

    def import_events(self, data: ClassroomBridgeImport) -> dict[str, int]:
        admin = self._admin()
        app_zone = ZoneInfo(self.settings.app_timezone)
        counts = {"created": 0, "updated": 0, "skipped": 0}

        try:
            for event in data.events:
                start = event.start
                if start.tzinfo is None:
                    start = start.replace(tzinfo=app_zone)
                synchronized = {
                    "title": event.title,
                    "description": event.description,
                    "category": data.subject_name,
                    "responsible": data.professor_name,
                    "due_date": start.astimezone(app_zone).date(),
                    "priority": TaskPriority.MEDIUM,
                    "status": TaskStatus.PENDING,
                    "created_by": admin.id,
                }
                task = self.db.scalar(
                    select(Task).where(
                        Task.source == TaskSource.CLASSROOM_BRIDGE,
                        Task.external_calendar_id == data.calendar_id,
                        Task.external_id == event.id,
                    )
                )
                if task:
                    for field, value in synchronized.items():
                        setattr(task, field, value)
                    counts["updated"] += 1
                else:
                    self.db.add(
                        Task(
                            **synchronized,
                            source=TaskSource.CLASSROOM_BRIDGE,
                            external_calendar_id=data.calendar_id,
                            external_id=event.id,
                        )
                    )
                    counts["created"] += 1
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return counts
