from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import admin_user, current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MemberInviteCreate,
    MemberInviteCreated,
    MemberInviteResponse,
    MemberRegistration,
    UserResponse,
)
from app.security.passwords import verify_password
from app.security.tokens import create_access_token
from app.services.member_invite_service import MemberInviteService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserResponse)
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)) -> User:
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas"
        )
    settings = get_settings()
    response.set_cookie(
        "taskflow_session",
        create_access_token(user.id),
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie("taskflow_session", path="/")


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(current_user)) -> User:
    return user


@router.post("/register-member", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_member(data: MemberRegistration, db: Session = Depends(get_db)) -> User:
    return MemberInviteService(db).register(data)


@router.post(
    "/member-invites", response_model=MemberInviteCreated, status_code=status.HTTP_201_CREATED
)
def create_member_invite(
    data: MemberInviteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_user),
) -> dict[str, object]:
    invite, token = MemberInviteService(db).create(data.email, user.id, data.expires_days)
    return {
        "id": invite.id,
        "email": invite.email,
        "expires_at": invite.expires_at,
        "used_at": invite.used_at,
        "created_at": invite.created_at,
        "created_by": invite.created_by,
        "invite_code": token,
    }


@router.get("/member-invites", response_model=list[MemberInviteResponse])
def list_member_invites(
    db: Session = Depends(get_db), _user: User = Depends(admin_user)
) -> list[object]:
    return MemberInviteService(db).list()
