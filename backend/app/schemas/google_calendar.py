from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GoogleCalendarItem(BaseModel):
    id: str
    name: str
    primary: bool = False


class GoogleCalendarSourceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    calendar_id: str = Field(min_length=1, max_length=255)
    subject_name: str = Field(min_length=1, max_length=80)
    professor_name: str | None = Field(default=None, max_length=100)
    enabled: bool = True


class GoogleCalendarSourceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject_name: str | None = Field(default=None, min_length=1, max_length=80)
    professor_name: str | None = Field(default=None, max_length=100)
    enabled: bool | None = None


class GoogleCalendarSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    calendar_id: str
    calendar_name: str
    subject_name: str
    professor_name: str | None
    enabled: bool
    last_synced_at: datetime | None
    last_error: str | None
    channel_expires_at: datetime | None


class GoogleCalendarStatus(BaseModel):
    connected: bool
    configured: bool
    account_email: str | None
    last_error: str | None
    sources: list[GoogleCalendarSourceResponse]


class GoogleOAuthConnectResponse(BaseModel):
    authorization_url: str


class GoogleSyncResult(BaseModel):
    created: int
    updated: int
    deleted: int
    skipped: int
