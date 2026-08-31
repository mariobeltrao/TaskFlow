"""Add member invites and Google Calendar integration.

Revision ID: 20260831_0002
Revises: 20260826_0001
"""

import sqlalchemy as sa

from alembic import op

revision = "20260831_0002"
down_revision = "20260826_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "member_invites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    op.create_index("ix_member_invites_email", "member_invites", ["email"])
    op.create_index("ix_member_invites_token_hash", "member_invites", ["token_hash"], unique=True)
    op.create_index("ix_member_invites_expires_at", "member_invites", ["expires_at"])

    op.create_table(
        "google_calendar_connections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("google_account_email", sa.String(255), nullable=False),
        sa.Column("encrypted_refresh_token", sa.Text(), nullable=False),
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
    )
    op.create_table(
        "google_calendar_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "connection_id",
            sa.Integer(),
            sa.ForeignKey("google_calendar_connections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("calendar_id", sa.String(255), nullable=False),
        sa.Column("calendar_name", sa.String(255), nullable=False),
        sa.Column("subject_name", sa.String(80), nullable=False),
        sa.Column("professor_name", sa.String(100), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("sync_token", sa.Text(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("channel_id", sa.String(64), nullable=True),
        sa.Column("channel_resource_id", sa.String(255), nullable=True),
        sa.Column("channel_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("connection_id", "calendar_id", name="uq_google_source_calendar"),
        sa.UniqueConstraint("channel_id", name="uq_google_calendar_sources_channel_id"),
    )
    op.create_index(
        "ix_google_calendar_sources_connection_id", "google_calendar_sources", ["connection_id"]
    )
    op.create_index("ix_google_calendar_sources_enabled", "google_calendar_sources", ["enabled"])

    with op.batch_alter_table("tasks") as batch_op:
        batch_op.add_column(
            sa.Column(
                "source",
                sa.Enum("MANUAL", "GOOGLE_CALENDAR", name="tasksource"),
                nullable=False,
                server_default="MANUAL",
            )
        )
        batch_op.add_column(sa.Column("external_id", sa.String(255), nullable=True))
        batch_op.add_column(sa.Column("external_calendar_id", sa.String(255), nullable=True))
        batch_op.add_column(
            sa.Column("external_updated_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.create_index("ix_tasks_source", ["source"])
        batch_op.create_unique_constraint(
            "uq_tasks_external_event", ["source", "external_calendar_id", "external_id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.drop_constraint("uq_tasks_external_event", type_="unique")
        batch_op.drop_index("ix_tasks_source")
        batch_op.drop_column("external_updated_at")
        batch_op.drop_column("external_calendar_id")
        batch_op.drop_column("external_id")
        batch_op.drop_column("source")
    op.drop_table("google_calendar_sources")
    op.drop_table("google_calendar_connections")
    op.drop_table("member_invites")
