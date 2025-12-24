from typing import Any, Generic, Literal, Optional, Type, TypeVar
from uuid import UUID

from fastapi import Query
from sqlmodel import SQLModel, select

from src.database.db import DBSession

ModelType = TypeVar("ModelType", bound=SQLModel)


class PaginationParams(SQLModel):
    offset: int = 1
    limit: int = Query(default=10, le=10)
    order_by: Literal["asc", "decs"] = "asc"


def get_pagination_params(
    offset: int = 1,
    limit: int = Query(default=10, le=10),
    order_by: Literal["asc", "decs"] = "asc",
):
    return PaginationParams(offset=offset, limit=limit, order_by=order_by)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: DBSession, model: Type[ModelType]):
        self.session = session
        self.model: Type[ModelType] = model

    async def get(self, pk: UUID) -> Optional[ModelType]:
        statement = select(self.model).where(self.model.id == pk)
        obj = await self.session.exec(statement=statement)
        return obj.unique().first()

    async def list(
        self,
        offset: int = 0,
        limit: int = Query(default=100, le=100),
        order_by: Literal["asc", "decs"] = "asc",
    ) -> list[ModelType]:
        statement = select(self.model).offset(offset).limit(limit)
        if order_by is not None:
            results = await self.session.exec(
                statement=select(self.model)
                .offset(offset)
                .limit(limit)
                .order_by(order_by)
            )
            return results.unique().fetchall()
        else:
            results = await self.session.exec(statement=statement)
            return results.unique().all()

    async def create(self, obj: ModelType) -> ModelType:
        db_obj = self.model(**obj.model_dump())
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, pk: UUID) -> UUID:
        instance = await self.get(pk=pk)
        await self.session.delete(instance)
        await self.session.commit()
        return pk

    async def update(
        self,
        obj_id: UUID,
        obj: ModelType | dict,
    ) -> Optional[ModelType]:
        instance = await self.get(pk=obj_id)

        obj_data = obj.model_dump(exclude_unset=True)
        instance.sqlmodel_update(obj_data)

        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)

        return instance

    async def patch(
        self,
        obj_id: UUID,
        obj: ModelType | dict,
    ) -> Optional[ModelType]:
        instance = await self.get(pk=obj_id)
        instance.sqlmodel_update(obj)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)

        return instance
