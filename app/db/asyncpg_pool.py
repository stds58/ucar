import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional


class AsyncPGDatabase:
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self, dsn: str, min_size: int = 10, max_size: int = 80):
        if self._pool is not None:
            return  # Уже подключено

        self._pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=min_size,
            max_size=max_size,
            command_timeout=5,
            statement_cache_size=0,  # Критично для PgBouncer
        )

    async def disconnect(self):
        if self._pool:
            await self._pool.close()
            self._pool = None

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        if self._pool is None:
            raise RuntimeError("Pool not initialized. Call connect() first.")
        async with self._pool.acquire() as conn:
            yield conn


# Создаем единственный экземпляр для всего приложения
asyncpg_db_client = AsyncPGDatabase()
