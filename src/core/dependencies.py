from typing import Annotated, AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from jose import JWTError
from redis.asyncio import Redis

from src.auth.service import AuthService
from src.core import security
from src.core.repositories.todo import TodoRepository
from src.database.db import DBSession
from src.database.redis import get_redis
from src.entities.user import User
from src.todos.service import TodoService
from src.users.service import UserService


def get_user_service(session: DBSession):
    return UserService(session=session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_todo_repo(session: DBSession) -> TodoRepository:
    return TodoRepository(session=session)


def get_todo_service(
    repository: TodoRepository = Depends(get_todo_repo),
) -> TodoService:
    return TodoService(repository)


TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]


def get_auth_service(session: DBSession):
    return AuthService(session=session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
    token: Annotated[dict, Depends(security.verify_access_token)],
    session: DBSession,
):
    try:
        # Cast the string ID to a UUID object
        user_id = UUID(token["user"]["user_id"])

        return await session.get(User, user_id)
    except (ValueError, TypeError):
        # Handles cases where the ID in the token is not a valid UUID
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token.",
        )
    except JWTError:
        # JWTError usually happens in verify_access_token,
        # but we keep it here if your logic requires it
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user.",
        )


UserDep = Annotated[User, Depends(get_current_user)]


async def get_redis_dependency() -> AsyncGenerator[Redis, None]:
    async with get_redis() as redis:
        yield redis
