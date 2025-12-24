
from uuid import UUID

from src.core.repositories.base import BaseRepository
from src.entities.user import User


class UserRepository:
    def __init__(self, session):
       self.repo = BaseRepository(session=session, model=User)

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.repo.get(user_id)

    async def get_all(self) -> list[User]:
        return await self.repo.list(skip=0, limit=100)