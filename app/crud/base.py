"""абстракция над крудами"""

from typing import ClassVar, Generic, List, Optional
from uuid import UUID
#import structlog
from app.core.async_logger import ainfo, aerror
from pydantic import BaseModel as PydanticModel
from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.base import ObjectsNotFoundByIDError
from app.crud.mixins.query_mixin import QueryMixin
from app.crud.mixins.types import (
    ModelType,
    CreateSchemaType,
    UpdateSchemaType,
    FilterSchemaType,
)
from concurrent.futures import ThreadPoolExecutor
import asyncio
from app.db.asyncpg_pool import get_asyncpg_pool


#logger = structlog.get_logger()

serialization_pool = ThreadPoolExecutor(max_workers=6)


class BaseDAO(
    QueryMixin, Generic[ModelType, CreateSchemaType, UpdateSchemaType, FilterSchemaType]
):
    """базовый класс"""

    model: ClassVar[type[ModelType]]
    create_schema: ClassVar[type[CreateSchemaType]]
    update_schema: ClassVar[type[UpdateSchemaType]]
    filter_schema: ClassVar[type[FilterSchemaType]]
    pydantic_model: ClassVar[type[PydanticModel]]

    @classmethod
    async def find_many_orm(
            cls, session: AsyncSession, filters: Optional[FilterSchemaType] = None
    ) -> List[PydanticModel]:
        """используем alchemy orm"""
        query = select(cls.model)
        query = cls._build_query(query, filters)
        result = await session.execute(query)
        results = result.unique().scalars().all()

        return [
            cls.pydantic_model.model_validate(obj, from_attributes=True)
            for obj in results
        ]

    @classmethod
    async def find_many_raw_sql(cls, session: AsyncSession) -> List[PydanticModel]:
        """используем alchemy core и asyncio.get_running_loop"""
        result = await session.execute(
            text("SELECT id, created_at, updated_at, description, "
                 "LOWER(status::TEXT) AS status, "
                 "LOWER(source::TEXT) AS source "
                 "FROM incident")
        )
        rows = result.fetchall()

        loop = asyncio.get_running_loop()
        # Выполняем сериализацию в отдельном потоке
        return await loop.run_in_executor(
            serialization_pool,
            lambda: [
                cls.pydantic_model.model_validate(row._mapping)
                for row in rows
            ]
        )

    @classmethod
    async def find_many_native(cls) -> List[dict]:
        """используем get_asyncpg_pool"""
        pool = await get_asyncpg_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                        SELECT id, created_at, updated_at, description,
                               status::TEXT AS status,
                               source::TEXT AS source
                        FROM incident
                    """)
        return [dict(r) for r in rows]

    @classmethod
    async def find_many_dummy(cls) -> List[dict]:
        """выводит 100 словарей. посгрес не используется"""
        return [{"id": i, "name": "test"} for i in range(100)]

    @classmethod
    async def add_one(
        cls, session: AsyncSession, values: CreateSchemaType
    ) -> PydanticModel:
        """добавить запись"""
        filters_dict = values.model_dump(exclude_unset=True)
        new_instance = cls.model(**filters_dict)
        session.add(new_instance)
        await session.flush()
        await session.refresh(new_instance)
        return cls.pydantic_model.model_validate(new_instance, from_attributes=True)

    @classmethod
    async def update_one(
        cls, model_id: UUID, values: UpdateSchemaType, session: AsyncSession
    ) -> PydanticModel:
        """обновить запись"""
        filters_dict = values.model_dump(exclude_unset=True)
        stmt = (
            update(cls.model)
            .where(cls.model.id == model_id)
            .values(**filters_dict)
            .returning(cls.model)
        )
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()

        if obj is None:
            await aerror(
                "ObjectsNotFoundByIDError on update",
                model_id=model_id,
                error="Запрашиваемый объект не найден",
            )
            raise ObjectsNotFoundByIDError

        return cls.pydantic_model.model_validate(obj, from_attributes=True)
