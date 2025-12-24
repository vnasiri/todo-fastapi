from fastapi import status
from src.exceptions import DomainError

class TodoError(DomainError):
    """Base exception for todo‑related errors."""

    entity = "Todo"

class TodoNotFoundError(TodoError):
    """Todo was not found."""
    def __init__(self, todo_id: str):
        super().__init__(
            detail=f"Todo with id '{todo_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class TodoAlreadyExistsError(TodoError):
    def __init__(self, title: str):
        super().__init__(
            detail=f"Todo with title '{title}' already exists.",
            status_code=status.HTTP_409_CONFLICT,
        )

