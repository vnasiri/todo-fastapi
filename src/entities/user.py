from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import EmailStr, field_validator
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from src.entities.todo import Todo  # noqa: F401


class Role(StrEnum):
    User = "user"
    Admin = "admin"


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    email: EmailStr = Field(max_length=255, unique=True, nullable=False, index=True)
    email_verified: bool = Field(default=False)
    username: str = Field(max_length=150, unique=True, nullable=False, index=True)
    password_hash: str = Field(nullable=False)
    first_name: str = Field(max_length=100, min_length=3)
    last_name: str = Field(max_length=100, min_length=3)
    is_active: bool = Field(default=True)
    role: "Role" = Field(default=Role.User.value)
    todos: list["Todo"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"lazy": "joined"},
    )
    __table_args__ = (
        UniqueConstraint("username", name="uq_user_username"),
        UniqueConstraint("email", name="uq_user_email"),
    )

    @field_validator("first_name", "last_name")
    def name_must_be_long_enough(cls, value: str) -> str:
        if len(value.strip()) < 5:
            raise ValueError("must contain at least 3 characters")
        return value
