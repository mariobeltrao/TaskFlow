from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClassroomBridgeEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    start: datetime
    end: datetime


class ClassroomBridgeImport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    calendar_id: str = Field(min_length=1, max_length=255)
    calendar_name: str = Field(min_length=1, max_length=255)
    subject_name: str = Field(min_length=1, max_length=80)
    professor_name: str | None = Field(default=None, max_length=100)
    events: list[ClassroomBridgeEvent]


class ClassroomBridgeImportResult(BaseModel):
    created: int
    updated: int
    skipped: int
