"""
Контекстный менеджер для создания сессии с опциональным уровнем изоляции.
Для гибкого управления уровнем изоляции
"""

from typing import Optional
import asyncio
from contextlib import asynccontextmanager
#import structlog
from app.core.async_logger import ainfo, aerror, awarning
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


#logger = structlog.get_logger()


def create_session_factory(database_url: str):
    """Создает фабрику сессий для заданного URL базы данных"""
    #engine = create_async_engine(database_url)
    engine = create_async_engine(
        database_url,
        pool_size=13,  # количество соединений в пуле
        max_overflow=3,  # количество "переполненных" соединений
        #pool_pre_ping=True,  # проверять соединение перед использованием
        #pool_recycle=300,  # пересоздавать соединение каждые 300 секунд
    )
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session_with_isolation(session_factory, isolation_level: Optional[str]):
    """
    Асинхронный контекстный менеджер для получения сессии с заданным уровнем изоляции.

    Args:
        session_factory: Фабрика для создания асинхронной сессии.
        isolation_level: Уровень изоляции транзакции (например, "READ COMMITTED").
                         Если None, используется уровень по умолчанию.

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy.

    Raises:
        ConnectionRefusedError: Если не удалось подключиться к БД.
        OSError: Если произошла системная ошибка.
        asyncio.TimeoutError: Если истекло время ожидания подключения.
    """
    try:
        async with session_factory() as session:
            yield session
    except (ConnectionRefusedError, OSError, asyncio.TimeoutError) as exc:
        await aerror(
            "Ошибка (ConnectionRefusedError, OSError, asyncio.TimeoutError)",
            error=str(exc),
        )
        raise
