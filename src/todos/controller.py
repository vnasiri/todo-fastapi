from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src.core.dependencies import TodoServiceDep, UserDep
from src.core.repositories.base import PaginationParams, get_pagination_params
from src.rate_limiting import limiter
from src.tags import APITags
from src.todos.models import TodoCreate, TodoPatch, TodoRead, TodoUpdate

APP_DIR = Path(__file__).resolve().parent.parent


router = APIRouter(prefix="/todos", tags=[APITags.TODOS])


@router.post(
    "/",
    response_model=TodoRead,
    status_code=status.HTTP_201_CREATED,
    description="Crating **todo**",
    responses={
        status.HTTP_201_CREATED: {
            "description": "The todo has been created successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request.",
        },
    },
)
@limiter.limit("60/minute")
async def create_todo(
    user_dep: UserDep, todo: TodoCreate, service: TodoServiceDep, request: Request
) -> TodoRead:
    return await service.create(todo, user_dep)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=list[TodoRead],
    name="todos",
)
@limiter.limit("60/minute")
async def todo_list(
    _: UserDep,
    service: TodoServiceDep,
    request: Request,
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
) -> list[TodoRead]:
    return await service.list(
        offset=pagination.offset, limit=pagination.limit, order_by=pagination.order_by
    )


@router.get("/{todo_id}", name="todo", description="Get a single todo")
@limiter.limit("60/minute")
async def read_todo(
    user: UserDep, todo_id: UUID, service: TodoServiceDep, request: Request
) -> TodoRead:
    todo = await service.read(todo_id)
    context = todo.model_dump()
    context["owner"] = user.username
    return todo


@router.put(
    "/{todo_id}",
    status_code=status.HTTP_200_OK,
    response_model=TodoRead,
    description="Update a **to-do**",
)
@limiter.limit("60/minute")
async def update_todo(
    _: UserDep,
    todo_id: UUID,
    todo: TodoUpdate,
    service: TodoServiceDep,
    request: Request,
):
    return await service.update(todo_id, todo)


@router.patch("/{todo_id}")
@limiter.limit("60/minute")
async def patch_todo(
    _: UserDep,
    todo_id: UUID,
    payload: TodoPatch,
    service: TodoServiceDep,
    request: Request,
):
    return await service.patch_todo(todo_id=todo_id, payload=payload)


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("60/minute")
async def delete_todo(
    _: UserDep,
    todo_id: UUID,
    service: TodoServiceDep,
    request: Request,
):
    await service.delete(todo_id)
    return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)
