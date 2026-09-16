from functools import lru_cache
from typing import Annotated

from pydantic import field_validator, model_validator
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
    enable_google_integration: bool = False
    google_calendar_sync_interval_minutes: int = 5
    classroom_bridge_token: str = ""
    classroom_bridge_admin_email: str = ""
    auth_rate_limit_attempts: int = 10
    auth_rate_limit_window_seconds: int = 300
    frontend_dist_dir: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def use_psycopg_driver(cls, value: object) -> object:
        if isinstance(value, str):
            if value.startswith("postgres://"):
                return value.replace("postgres://", "postgresql+psycopg://", 1)
            if value.startswith("postgresql://"):
                return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @model_validator(mode="after")
    def validate_production(self) -> "Settings":
        if self.environment.lower() != "production":
            return self
        if not self.secret_key or self.secret_key == "development-only-change-me":
            raise ValueError("SECRET_KEY forte é obrigatória em produção")
        if self.database_url.startswith("sqlite"):
            raise ValueError("SQLite não é permitido em produção; configure PostgreSQL")
        if not self.cookie_secure:
            raise ValueError("COOKIE_SECURE deve ser true em produção")
        if not self.frontend_url.startswith("https://"):
            raise ValueError("FRONTEND_URL deve usar HTTPS em produção")
        if "*" in self.cors_origins:
            raise ValueError("CORS_ORIGINS não pode conter * em produção")
        allowed_origins = {origin.rstrip("/") for origin in self.cors_origins}
        if self.frontend_url.rstrip("/") not in allowed_origins:
            raise ValueError("CORS_ORIGINS deve incluir FRONTEND_URL em produção")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
