from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.member_invite import MemberInvite
from app.models.user import User
from app.schemas.auth import MemberRegistration
from app.security.invite_tokens import create_invite_token, hash_invite_token
from app.security.passwords import hash_password


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class MemberInviteService:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, email: str, created_by: int, expires_days: int = 7
    ) -> tuple[MemberInvite, str]:
        normalized_email = email.lower()
        if self.db.scalar(select(User.id).where(User.email == normalized_email)):
            raise HTTPException(status_code=409, detail="E-mail já cadastrado")
        token = create_invite_token()
        invite = MemberInvite(
            email=normalized_email,
            token_hash=hash_invite_token(token),
            expires_at=datetime.now(UTC) + timedelta(days=expires_days),
            created_by=created_by,
        )
        self.db.add(invite)
        self.db.commit()
        self.db.refresh(invite)
        return invite, token

    def list(self) -> list[MemberInvite]:
        return list(self.db.scalars(select(MemberInvite).order_by(MemberInvite.created_at.desc())))

    def register(self, data: MemberRegistration) -> User:
        normalized_email = data.email.lower()
        invite = self.db.scalar(
            select(MemberInvite).where(
                MemberInvite.token_hash == hash_invite_token(data.invite_code)
            )
        )
        if not invite or invite.email != normalized_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Convite inválido")
        if invite.used_at is not None:
            raise HTTPException(status_code=400, detail="Convite já utilizado")
        if _as_utc(invite.expires_at) <= datetime.now(UTC):
            raise HTTPException(status_code=400, detail="Convite expirado")
        if self.db.scalar(select(User.id).where(User.email == normalized_email)):
            raise HTTPException(status_code=409, detail="E-mail já cadastrado")

        user = User(
            name=data.name.strip(),
            email=normalized_email,
            password_hash=hash_password(data.password),
            role=UserRole.MEMBER,
        )
        invite.used_at = datetime.now(UTC)
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(status_code=409, detail="E-mail já cadastrado") from exc
        self.db.refresh(user)
        return user
