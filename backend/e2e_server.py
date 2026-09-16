"""Servidor isolado e descartável usado exclusivamente pelos testes Playwright."""

import atexit
import os
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

database_fd, database_name = tempfile.mkstemp(prefix="taskflow-e2e-", suffix=".sqlite3")
os.close(database_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{Path(database_name).as_posix()}"
os.environ["SECRET_KEY"] = "e2e-only-secret-key-with-at-least-thirty-two-characters"
os.environ["CORS_ORIGINS"] = "http://127.0.0.1:4173"
os.environ["GOOGLE_TOKEN_ENCRYPTION_KEY"] = (
    "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="
)

from app.db.session import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.enums import TaskPriority, TaskStatus, UserRole  # noqa: E402
from app.models.member_invite import MemberInvite  # noqa: E402
from app.models.task import Task  # noqa: E402
from app.models.user import User  # noqa: E402
from app.security.invite_tokens import hash_invite_token  # noqa: E402
from app.security.passwords import hash_password  # noqa: E402

INVITE_CODE = "taskflow-e2e-invite-code-0000000000000001"
Base.metadata.create_all(engine)
with SessionLocal() as db:
    admin = User(
        name="Admin E2E",
        email="admin.e2e@example.com",
        password_hash=hash_password("password123"),
        role=UserRole.ADMIN,
    )
    member = User(
        name="Aluno E2E",
        email="member.e2e@example.com",
        password_hash=hash_password("password123"),
        role=UserRole.MEMBER,
    )
    db.add_all([admin, member])
    db.flush()
    db.add(
        Task(
            title="Tarefa compartilhada",
            category="E2E",
            due_date=datetime.now().date(),
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            created_by=admin.id,
        )
    )
    db.add(
        MemberInvite(
            email="new-member.e2e@example.com",
            token_hash=hash_invite_token(INVITE_CODE),
            expires_at=datetime.now(UTC) + timedelta(days=1),
            created_by=admin.id,
        )
    )
    db.commit()


@atexit.register
def cleanup_database() -> None:
    engine.dispose()
    Path(database_name).unlink(missing_ok=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
