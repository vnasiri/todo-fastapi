from uuid import UUID

from pydantic import EmailStr, Field
from sqlmodel import SQLModel

from src.entities.user import Role


class UserCreate(SQLModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    username: str = Field(max_length=100)
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=12, max_length=100)
    role: "Role" = Field(default=Role.User.value)


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenPayload(SQLModel):
    user_id: str | None = None
    jti: str | None = None
