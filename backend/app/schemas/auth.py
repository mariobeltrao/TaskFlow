from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models.enums import UserRole


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: UserRole


class MemberRegistration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    invite_code: str = Field(min_length=32, max_length=128)
    password: str = Field(min_length=8, max_length=128)
    password_confirmation: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def passwords_match(self) -> "MemberRegistration":
        if self.password != self.password_confirmation:
            raise ValueError("As senhas não coincidem")
        return self


class MemberInviteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    expires_days: int = Field(default=7, ge=1, le=90)


class MemberInviteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    expires_at: datetime
    used_at: datetime | None
    created_at: datetime
    created_by: int


class MemberInviteCreated(MemberInviteResponse):
    invite_code: str
