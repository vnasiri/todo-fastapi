from datetime import datetime
from enum import IntEnum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from src.entities.user import User
    from src.todos.models import TodoCreate


class Priority(IntEnum):
    Low = 0
    Medium = 1
    High = 2
    Critical = 3


class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        ),
    )
    title: str = Field(nullable=False, max_length=50)
    description: str = Field(nullable=False, max_length=255)
    is_completed: bool = Field(nullable=False, default=False)
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )
    priority: "Priority" = Field(nullable=False, default=Priority.Medium.value)
    owner_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        ondelete="CASCADE",
        index=True,
    )
    owner: "User" = Relationship(
        back_populates="todos",
        sa_relationship_kwargs={"lazy": "joined"},
    )
    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            "title",
            name="uq_user_title",
        ),
    )

    @staticmethod
    def from_create_model(todo_create: "TodoCreate", owner_id: UUID) -> "Todo":
        """
        Build a Todo ORM object from a validated TodoCreate schema.
        This method does **not** need any instance data.
        """
        return Todo(**todo_create.model_dump(), owner_id=owner_id)
