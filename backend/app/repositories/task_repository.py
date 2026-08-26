from datetime import date, timedelta

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import TaskPriority, TaskStatus
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

PRIORITY_ORDER = case(
    (Task.priority == TaskPriority.URGENT, 4),
    (Task.priority == TaskPriority.HIGH, 3),
    (Task.priority == TaskPriority.MEDIUM, 2),
    else_=1,
)


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def list(
        self,
        *,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        category: str | None = None,
        search: str | None = None,
        overdue: bool = False,
        upcoming: bool = False,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Task], int]:
        today = date.today()
        filters = []
        if status:
            filters.append(Task.status == status)
        if priority:
            filters.append(Task.priority == priority)
        if category:
            filters.append(Task.category == category)
        if search:
            filters.append(Task.title.ilike(f"%{search}%"))
        if date_from:
            filters.append(Task.due_date >= date_from)
        if date_to:
            filters.append(Task.due_date <= date_to)
        if overdue:
            filters.extend([Task.status == TaskStatus.PENDING, Task.due_date < today])
        if upcoming:
            filters.extend(
                [
                    Task.status == TaskStatus.PENDING,
                    Task.due_date >= today,
                    Task.due_date <= today + timedelta(days=7),
                ]
            )
        pending_rank = case((Task.status == TaskStatus.PENDING, 0), else_=1)
        overdue_rank = case(
            (or_(Task.status == TaskStatus.COMPLETED, Task.due_date >= today), 1), else_=0
        )
        query = (
            select(Task)
            .where(*filters)
            .order_by(
                pending_rank,
                overdue_rank,
                Task.due_date.asc(),
                PRIORITY_ORDER.desc(),
                Task.created_at.asc(),
            )
        )
        total = self.db.scalar(select(func.count()).select_from(Task).where(*filters)) or 0
        items = list(self.db.scalars(query.offset((page - 1) * page_size).limit(page_size)))
        return items, total

    def create(self, data: TaskCreate, user_id: int) -> Task:
        task = Task(**data.model_dump(), created_by=user_id)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: Task, data: TaskUpdate) -> Task:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
