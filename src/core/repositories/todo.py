from uuid import UUID
from sqlmodel import asc, desc

from src.core.repositories.base import BaseRepository
from src.entities.todo import Todo
from src.todos.models import TodoCreate, TodoDelete, TodoRead, TodoUpdate, TodoPatch


class TodoRepository:
    def __init__(self, session):
        self.repository = BaseRepository(session=session, model=Todo)

    async def get_all(
        self, limit: int = 10, offset: int = 0, order_by: str = "asc"
    ) -> list[TodoRead]:
        return await self.repository.list(
            offset=offset,
            limit=limit,
            order_by=(asc(Todo.created_at))
            if order_by == "asc"
            else desc(Todo.created_at),
        )

    async def get_by_id(self, todo_id: UUID) -> TodoRead:
        todo = await self.repository.get(pk=todo_id)
        return TodoRead.model_validate(todo)

    async def create(self, payload: TodoCreate, owner_id: UUID) -> TodoRead:
        todo = Todo.from_create_model(payload, owner_id=owner_id)
        new_todo = await self.repository.create(todo)
        return TodoRead.model_validate(new_todo)

    async def update(self, todo_id: UUID, payload: TodoUpdate) -> TodoRead:
        """Update todo with title, description, and/or priority - does NOT update is_completed"""
        updated = await self.repository.update(
            obj_id=todo_id,
            obj=payload,
        )
        return TodoRead.model_validate(updated, from_attributes=True)

    async def patch_todo(self, todo_id: UUID, data: TodoPatch) -> TodoRead:
        """Partial update - ONLY for toggling is_completed status"""
        return await self.repository.patch(todo_id, data)

    async def delete(self, todo_id: UUID) -> TodoDelete:
        """
        Delete the row and return a minimal delete‑schema (containing the id).
        """
        await self.repository.delete(pk=todo_id)
        return TodoDelete(id=todo_id)
