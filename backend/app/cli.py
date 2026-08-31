import argparse
import getpass
import os
from datetime import date, timedelta

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.enums import TaskPriority, TaskStatus, UserRole
from app.models.task import Task
from app.models.user import User
from app.security.passwords import hash_password
from app.services.member_invite_service import MemberInviteService


def create_admin(email: str, name: str) -> None:
    password = os.getenv("TASKFLOW_ADMIN_PASSWORD") or getpass.getpass(
        "Senha (mín. 8 caracteres): "
    )
    if len(password) < 8:
        raise SystemExit("A senha deve ter pelo menos 8 caracteres.")
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == email.lower())):
            raise SystemExit("E-mail já cadastrado.")
        db.add(
            User(
                name=name,
                email=email.lower(),
                password_hash=hash_password(password),
                role=UserRole.ADMIN,
            )
        )
        db.commit()
    print("Administrador criado com segurança.")


def seed() -> None:
    with SessionLocal() as db:
        admin = db.scalar(select(User).where(User.role == UserRole.ADMIN))
        if not admin:
            raise SystemExit("Crie um administrador antes do seed.")
        if db.scalar(select(Task.id).limit(1)):
            raise SystemExit("O banco já possui tarefas.")
        today = date.today()
        rows = [
            (
                "Entregar projeto final",
                "Programação",
                today + timedelta(days=1),
                TaskPriority.URGENT,
                TaskStatus.PENDING,
            ),
            (
                "Lista de exercícios",
                "Matemática",
                today + timedelta(days=6),
                TaskPriority.HIGH,
                TaskStatus.PENDING,
            ),
            (
                "Revisar capítulo 4",
                "História",
                today - timedelta(days=3),
                TaskPriority.MEDIUM,
                TaskStatus.PENDING,
            ),
            (
                "Resumo de biologia",
                "Biologia",
                today - timedelta(days=1),
                TaskPriority.LOW,
                TaskStatus.COMPLETED,
            ),
        ]
        db.add_all(
            [
                Task(title=t, category=c, due_date=d, priority=p, status=s, created_by=admin.id)
                for t, c, d, p, s in rows
            ]
        )
        db.commit()
    print("Dados de demonstração criados.")


def create_member_invite(email: str, expires_days: int, admin_email: str | None) -> None:
    with SessionLocal() as db:
        query = select(User).where(User.role == UserRole.ADMIN)
        if admin_email:
            query = query.where(User.email == admin_email.lower())
        admin = db.scalar(query.order_by(User.created_at))
        if not admin:
            raise SystemExit("Administrador não encontrado.")
        try:
            invite, token = MemberInviteService(db).create(email, admin.id, expires_days)
        except Exception as exc:
            detail = getattr(exc, "detail", str(exc))
            raise SystemExit(detail) from exc
    print(f"Convite criado para {invite.email}; expira em {invite.expires_at.isoformat()}.")
    print("Código (exibido somente agora):")
    print(token)


def sync_google_calendar() -> None:
    from app.services.google_calendar_service import GoogleCalendarService

    with SessionLocal() as db:
        result = GoogleCalendarService(db).sync_all()
    print(
        "Sincronização concluída: "
        f"{result['created']} criadas, {result['updated']} atualizadas, "
        f"{result['deleted']} removidas e {result['skipped']} ignoradas."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    admin = sub.add_parser("create-admin")
    admin.add_argument("--email", required=True)
    admin.add_argument("--name", required=True)
    invite = sub.add_parser("create-member-invite")
    invite.add_argument("--email", required=True)
    invite.add_argument("--expires-days", type=int, default=7)
    invite.add_argument("--admin-email")
    sub.add_parser("sync-google-calendar")
    sub.add_parser("seed")
    args = parser.parse_args()
    if args.command == "create-admin":
        create_admin(args.email, args.name)
    elif args.command == "create-member-invite":
        create_member_invite(args.email, args.expires_days, args.admin_email)
    elif args.command == "sync-google-calendar":
        sync_google_calendar()
    else:
        seed()
