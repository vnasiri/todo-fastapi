from typing import Optional
from uuid import UUID

from pydantic import ConfigDict, EmailStr, Field
from sqlmodel import SQLModel

from src.entities.user import Role


class UserUpdate(SQLModel):
    email: Optional[EmailStr] | None = Field(default=None)
    first_name: str
    last_name: str


class UserResponse(SQLModel):
    id: UUID
    username: str
    email: EmailStr
    role: "Role" = Field(default=Role.User.value)
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "johndoe",
                    "email": "john.doe@example.com",
                    "role": Role.User.value,
                }
            ]
        },
    )


class PasswordChange(SQLModel):
    current_password: str
    new_password: str
    new_password_confirm: str


class UserPublic(SQLModel):
    id: UUID
