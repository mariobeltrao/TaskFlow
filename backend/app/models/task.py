from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import TaskPriority, TaskSource, TaskStatus


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_status_due_date", "status", "due_date"),
        Index("ix_tasks_category", "category"),
        UniqueConstraint(
            "source", "external_calendar_id", "external_id", name="uq_tasks_external_event"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(80))
    responsible: Mapped[str | None] = mapped_column(String(100), nullable=True)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), index=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING, index=True
    )
    source: Mapped[TaskSource] = mapped_column(
        Enum(TaskSource), default=TaskSource.MANUAL, index=True
    )
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_calendar_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    creator = relationship("User", back_populates="tasks")
