from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TaskFlow API"
    environment: str = "development"
    database_url: str = "sqlite:///./taskflow.db"
    secret_key: str = "development-only-change-me"
    access_token_expire_minutes: int = 480
    cookie_secure: bool = False
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]
    frontend_url: str = "http://localhost:5173"
    app_timezone: str = "America/Fortaleza"
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/integrations/google-calendar/callback"
    google_calendar_webhook_url: str = ""
    google_calendar_webhook_token: str = ""
    google_token_encryption_key: str = ""
    google_calendar_sync_enabled: bool = False
    google_calendar_sync_interval_minutes: int = 5
    classroom_bridge_token: str = ""
    classroom_bridge_admin_email: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
