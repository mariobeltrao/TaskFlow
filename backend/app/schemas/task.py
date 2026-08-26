from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    category: str = Field(min_length=1, max_length=80)
    responsible: str | None = Field(default=None, max_length=100)
    due_date: date
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    responsible: str | None = Field(default=None, max_length=100)
    due_date: date | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None


class TaskResponse(TaskCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime


class TaskPage(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int


class DashboardSummary(BaseModel):
    total_tasks: int
    pending_tasks: int
    completed_tasks: int
    upcoming_tasks: int
    overdue_tasks: int
    by_priority: dict[str, int]
    by_category: dict[str, int]
