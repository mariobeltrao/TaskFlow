from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import get_settings


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": str(user_id), "exp": expires}, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        return None


def create_oauth_state(user_id: int) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=10)
    return jwt.encode(
        {"sub": str(user_id), "purpose": "google-calendar-oauth", "exp": expires},
        get_settings().secret_key,
        algorithm="HS256",
    )


def decode_oauth_state(token: str) -> int | None:
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
        if payload.get("purpose") != "google-calendar-oauth":
            return None
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        return None
