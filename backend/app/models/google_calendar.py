from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class GoogleCalendarConnection(Base):
    __tablename__ = "google_calendar_connections"

    id: Mapped[int] = mapped_column(primary_key=True)
    google_account_email: Mapped[str] = mapped_column(String(255))
    encrypted_refresh_token: Mapped[str] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    sources = relationship(
        "GoogleCalendarSource", back_populates="connection", cascade="all, delete-orphan"
    )


class GoogleCalendarSource(Base):
    __tablename__ = "google_calendar_sources"
    __table_args__ = (
        UniqueConstraint("connection_id", "calendar_id", name="uq_google_source_calendar"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    connection_id: Mapped[int] = mapped_column(
        ForeignKey("google_calendar_connections.id", ondelete="CASCADE"), index=True
    )
    calendar_id: Mapped[str] = mapped_column(String(255))
    calendar_name: Mapped[str] = mapped_column(String(255))
    subject_name: Mapped[str] = mapped_column(String(80))
    professor_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    sync_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    channel_id: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    channel_resource_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    channel_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    connection = relationship("GoogleCalendarConnection", back_populates="sources")
