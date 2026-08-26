from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import TaskStatus
from app.models.task import Task
from app.repositories.task_repository import TaskRepository


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.tasks = TaskRepository(db)

    def summary(self) -> dict[str, object]:
        today = date.today()
        week = today + timedelta(days=7)
        counts = {
            "total_tasks": self._count(),
            "pending_tasks": self._count(Task.status == TaskStatus.PENDING),
            "completed_tasks": self._count(Task.status == TaskStatus.COMPLETED),
            "upcoming_tasks": self._count(
                Task.status == TaskStatus.PENDING, Task.due_date >= today, Task.due_date <= week
            ),
            "overdue_tasks": self._count(Task.status == TaskStatus.PENDING, Task.due_date < today),
        }
        priority_rows = self.db.execute(
            select(Task.priority, func.count()).group_by(Task.priority)
        ).all()
        category_rows = self.db.execute(
            select(Task.category, func.count()).group_by(Task.category).order_by(Task.category)
        ).all()
        counts["by_priority"] = {priority.value: count for priority, count in priority_rows}
        counts["by_category"] = dict(category_rows)
        return counts

    def _count(self, *filters: object) -> int:
        return self.db.scalar(select(func.count()).select_from(Task).where(*filters)) or 0
