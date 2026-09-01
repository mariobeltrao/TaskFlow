"""Add Classroom Bridge task source.

Revision ID: 20260901_0003
Revises: 20260831_0002
"""

from alembic import op

revision = "20260901_0003"
down_revision = "20260831_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE tasksource ADD VALUE IF NOT EXISTS 'CLASSROOM_BRIDGE'")
    elif bind.dialect.name in {"mysql", "mariadb"}:
        op.execute(
            "ALTER TABLE tasks MODIFY source "
            "ENUM('MANUAL', 'GOOGLE_CALENDAR', 'CLASSROOM_BRIDGE') NOT NULL DEFAULT 'MANUAL'"
        )


def downgrade() -> None:
    # Removing a PostgreSQL enum value would require rebuilding the type and could
    # destroy valid Classroom Bridge tasks. Keep the additive value on downgrade.
    pass
