"""
Фабрика зависимости
"""

from typing import AsyncGenerator
#import structlog
from structlog.contextvars import bind_contextvars
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import create_session_factory, get_session_with_isolation
from app.exceptions.base import (
    IntegrityErrorException,
    CustomInternalServerException,
    SqlalchemyErrorException,
    DatabaseConnectionException,
    SerializationFailureException,
)


#logger = structlog.get_logger()
async_session_maker = create_session_factory(settings.DATABASE_URL)


def connection():
    """
    Фабрика зависимости для FastAPI, создающая асинхронную сессию с заданным уровнем изоляции.
    """

    async def dependency() -> AsyncGenerator[AsyncSession, None]:
        async with get_session_with_isolation(
            async_session_maker, isolation_level="READ COMMITTED"
        ) as session:
            #session_id_obj = await session.execute(text("SELECT pg_backend_pid()"))
            #session_id = session_id_obj.scalar_one()
            #transaction_id_obj = await session.execute(text("SELECT txid_current()"))
            #transaction_id = transaction_id_obj.scalar()
            try:
                # bind_contextvars(
                #     session_id=session_id,
                #     transaction_id=transaction_id,
                # )
                yield session
            except IntegrityError as exc:
                #logger.error("IntegrityError", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise IntegrityErrorException from exc
            except OperationalError as exc:
                # Проверяем, является ли ошибка serialization failure
                if hasattr(exc.orig, "pgcode") and exc.orig.pgcode == "40001":
                    # logger.warning(
                    #     "Serialization failure (40001), should retry transaction"
                    # )
                    if session.in_transaction():
                        await session.rollback()
                    # Но здесь нельзя просто "повторить" — нужно перезапустить ВСЮ транзакцию
                    raise SerializationFailureException from exc
                #logger.error("OperationalError (non-serialization)", error=str(exc))
                raise DatabaseConnectionException from exc
            except (ConnectionRefusedError, OSError) as exc:
                #logger.error("ConnectionRefusedError, OSError", error=str(exc))
                raise CustomInternalServerException from exc
            except SQLAlchemyError as exc:
                #logger.error(" SQLAlchemyError", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise SqlalchemyErrorException from exc
            except Exception as exc:
                #logger.error("Other exception", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise

    return dependency
