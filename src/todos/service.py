from typing import TYPE_CHECKING
from uuid import UUID

from src.core.repositories.todo import TodoRepository
from src.todos import exceptions
from src.todos.models import TodoCreate, TodoDelete, TodoPatch, TodoRead, TodoUpdate

if TYPE_CHECKING:
    from src.core.dependencies import UserDep


class TodoService:
    def __init__(self, repo: TodoRepository):
        self.repo = repo

    async def read(self, todo_id: UUID) -> TodoRead:
        try:
            return await self.repo.get_by_id(todo_id)
        except Exception:
            raise exceptions.TodoNotFoundError(todo_id=todo_id)

    async def list(
        self, offset: int = 0, limit: int = 10, order_by: str = "asc"
    ) -> list[TodoRead]:
        return await self.repo.get_all(offset=offset, limit=limit, order_by=order_by)

    async def create(
        self,
        payload: TodoCreate,
        user: "UserDep",
    ) -> TodoRead:
        try:
            return await self.repo.create(
                payload=payload,
                owner_id=user.id,
            )
        except exceptions.TodoError as e:
            raise e

    async def update(
        self,
        todo_id: UUID,
        payload: TodoUpdate,
    ) -> TodoRead:
        try:
            return await self.repo.update(todo_id, payload)
        except Exception as e:
            raise exceptions.TodoNotFoundError(todo_id=todo_id) from e

    async def patch_todo(self, todo_id: UUID, payload: TodoPatch):
        try:
            return await self.repo.patch_todo(todo_id, payload)
        except Exception as e:
            raise e

    async def delete(self, todo_id: UUID) -> TodoDelete:
        try:
            return await self.repo.delete(todo_id)
        except Exception as e:
            raise exceptions.TodoNotFoundError(todo_id=todo_id) from e
