import asyncpg
from typing import Optional

_asyncpg_pool: Optional[asyncpg.Pool] = None

async def get_asyncpg_pool() -> asyncpg.Pool:
    global _asyncpg_pool
    if _asyncpg_pool is None:
        raise RuntimeError("Asyncpg pool not initialized")
    return _asyncpg_pool

async def init_asyncpg_pool(dsn: str, min_size: int = 10, max_size: int = 80):
    global _asyncpg_pool
    _asyncpg_pool = await asyncpg.create_pool(
        dsn=dsn,
        min_size=min_size,
        max_size=max_size,
        command_timeout=5,
        # Важно для PgBouncer в transaction mode:
        statement_cache_size=0,  # отключает prepared statements
    )

async def close_asyncpg_pool():
    global _asyncpg_pool
    if _asyncpg_pool:
        await _asyncpg_pool.close()
        _asyncpg_pool = None
