import asyncio
from concurrent.futures import ThreadPoolExecutor
from structlog import get_logger


# Один поток для всех логов — этого достаточно
_LOG_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="AsyncLogThread")


def _log(level: str, event: str, kwargs: dict):
    """Вызывает логгер в потоке."""
    logger = get_logger()
    log_method = getattr(logger, level)
    log_method(event, **kwargs)


async def ainfo(event: str, **kwargs):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(_LOG_EXECUTOR, _log, "info", event, kwargs)


async def aerror(event: str, **kwargs):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(_LOG_EXECUTOR, _log, "error", event, kwargs)


async def awarning(event: str, **kwargs):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(_LOG_EXECUTOR, _log, "warning", event, kwargs)


async def adebug(event: str, **kwargs):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(_LOG_EXECUTOR, _log, "debug", event, kwargs)


# Опционально: graceful shutdown
def shutdown():
    _LOG_EXECUTOR.shutdown(wait=True)
