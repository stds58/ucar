"""базовый класс моделей"""

from datetime import datetime
from typing import Annotated
from uuid import UUID
from sqlalchemy import DateTime, func, UUID as SQLAlchemyUUID, true, false, text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column, declared_attr, Mapped


# настройка аннотаций
# pylint: disable=invalid-name
IntPk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
UUIDPk = Annotated[
    UUID,
    mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=None,
        server_default=text("gen_random_uuid()"),
    ),
]
StrUniq = Annotated[str, mapped_column(unique=True, nullable=False)]
StrNullFalse = Annotated[str, mapped_column(nullable=False)]
StrNullTrue = Annotated[str, mapped_column(nullable=True)]
# pylint: disable=not-callable
CreatedAt = Annotated[
    datetime, mapped_column(DateTime(timezone=True), server_default=func.now())
]
UpdatedAt = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    ),
]
# pylint: enable=not-callable
BoolDefTrue = Annotated[
    bool, mapped_column(default=True, server_default=true(), nullable=False)
]
BoolDefFalse = Annotated[
    bool, mapped_column(default=False, server_default=false(), nullable=False)
]
# pylint: enable=invalid-name


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUIDPk]
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    @declared_attr.directive
    # pylint: disable-next=no-self-argument
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
