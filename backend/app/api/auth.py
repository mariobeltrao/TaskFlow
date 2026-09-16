from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
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
from app.security.http import auth_rate_limiter
from app.security.passwords import verify_password
from app.security.tokens import create_access_token
from app.services.member_invite_service import MemberInviteService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserResponse)
def login(
    data: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)
) -> User:
    settings = get_settings()
    client_host = request.client.host if request.client else "unknown"
    if not auth_rate_limiter.check(
        f"login:{client_host}",
        settings.auth_rate_limit_attempts,
        settings.auth_rate_limit_window_seconds,
    ):
        raise HTTPException(status_code=429, detail="Muitas tentativas; tente novamente mais tarde")
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas"
        )
    auth_rate_limiter.reset(f"login:{client_host}")
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
    settings = get_settings()
    response.delete_cookie(
        "taskflow_session", path="/", secure=settings.cookie_secure, httponly=True, samesite="lax"
    )


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(current_user)) -> User:
    return user


@router.post("/register-member", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_member(
    data: MemberRegistration, request: Request, db: Session = Depends(get_db)
) -> User:
    settings = get_settings()
    client_host = request.client.host if request.client else "unknown"
    if not auth_rate_limiter.check(
        f"register:{client_host}",
        settings.auth_rate_limit_attempts,
        settings.auth_rate_limit_window_seconds,
    ):
        raise HTTPException(status_code=429, detail="Muitas tentativas; tente novamente mais tarde")
    user = MemberInviteService(db).register(data)
    auth_rate_limiter.reset(f"register:{client_host}")
    return user


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
