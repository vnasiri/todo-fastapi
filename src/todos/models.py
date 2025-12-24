from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import ConfigDict, field_validator
from sqlmodel import Field, SQLModel

from src.entities.todo import Priority


class TodoCreate(SQLModel):
    """Model for creating a new todo item."""

    title: str = Field(max_length=100)
    description: str = Field(max_length=500)
    is_completed: bool = Field(default=False)
    priority: "Priority" = Field(default=Priority.Medium.value)
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Go shopping",
                    "description": "Buying Milk and Bread",
                    "prority": 1,
                    "is_completed": False,
                }
            ]
        }
    }

    @field_validator("title", "description")
    @classmethod
    def lenght_must_be_long_enough(cls, value: str) -> str:
        if len(value.strip()) < 10:
            raise ValueError("must contain at least 10 characters")
        return value


class TodoRead(SQLModel):
    id: UUID
    owner_id: UUID
    title: str
    description: str
    priority: "Priority"
    is_completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, frozen=True)


class TodoUpdate(SQLModel):
    """Model for updating todo - does NOT include is_completed"""

    title: Optional[str] = None
    description: Optional[str] = None
    priority: "Priority" = Field(default=Priority.Medium.value)
    model_config = ConfigDict(from_attributes=True)


class TodoPatch(SQLModel):
    """Model for partial updates - ONLY for toggling completion status"""

    is_completed: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)


class TodoDelete(SQLModel):
    id: UUID
    model_config = ConfigDict(frozen=True)
