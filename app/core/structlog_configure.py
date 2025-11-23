"""
structlog.stdlib.add_logger_name,
    добавляет поле "logger" с именем логгера
    (например, "__main__" или "myapp.api")
structlog.stdlib.PositionalArgumentsFormatter(),
    обрабатывает логи вида logger.info("Hello %s", "world") - превращает в "Hello world"
structlog.processors.StackInfoRenderer(),
    добавляет стек-трейс при вызове logger.info("msg", stack_info=True)
structlog.processors.format_exc_info,
    если в лог передано исключение (например, logger.error("Oops", exc_info=True)),
    он красиво форматирует traceback
"""

import os
import sys
import logging
import structlog
from structlog.processors import CallsiteParameterAdder, CallsiteParameter
from structlog.contextvars import merge_contextvars
from app.core.config import settings


def ordered_json_processor(logger, method_name, event_dict):  # pylint: disable=unused-argument
    """
    Формирует event_dict с фиксированным порядком ключей.
    Сначала системные поля, потом всё остальное.
    """
    # Определяем желаемый порядок "системных" полей
    system_keys = [
        "trace_id",
        "session_id",
        "transaction_id",
        "ip",
        "method",
        "path",
        "status",
        "process_time",
        "timestamp",
        "level",
        "logger",
        "filename",
        "func_name",
        "lineno",
        "event",
        "error",
        "model_id",
        "data",
        "filters",
        "commit",
        "worker_pid",
    ]

    # Создаём упорядоченный словарь
    ordered = {}

    # Сначала добавляем системные ключи (если есть)
    for key in system_keys:
        if key in event_dict:
            ordered[key] = event_dict.pop(key)

    # Затем добавляем всё остальное (в порядке появления или sorted)
    # Здесь просто добавляем остаток — порядок не важен
    ordered.update(event_dict)

    return ordered


def add_worker_pid(logger, method_name, event_dict):  # pylint: disable=unused-argument
    event_dict["worker_pid"] = os.getpid()
    return event_dict


def unify_log_level(logger, method_name, event_dict):  # pylint: disable=unused-argument
    """
    Унифицирует поле уровня лога в 'level'.
    Поддерживает как 'level', так и 'severity' на входе.
    """
    # Если уже есть 'level' — оставляем
    if "level" in event_dict:
        return event_dict

    # Если есть 'severity' — используем его как 'level'
    if "severity" in event_dict:
        # Приводим к нижнему регистру, как делает structlog по умолчанию
        event_dict["level"] = str(event_dict.pop("severity")).lower()
        return event_dict

    # Если ничего нет — ставим 'info' (или другой уровень по умолчанию)
    event_dict["level"] = "info"
    return event_dict


def configure_logging():
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # logging.basicConfig(
    #     format="%(message)s",
    #     stream=sys.stdout,
    #     level=log_level,
    # )

    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=[logging.FileHandler("/dev/null")],
    )

    structlog.configure(
        processors=[
            merge_contextvars,
            structlog.stdlib.add_log_level,
            unify_log_level,
            # CallsiteParameterAdder(
            #     [
            #         CallsiteParameter.FILENAME,
            #         CallsiteParameter.FUNC_NAME,
            #         CallsiteParameter.LINENO,
            #     ]
            # ),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            add_worker_pid,  # PID воркера
            structlog.processors.dict_tracebacks, # traceback становится частью JSON и виден в Kibane
            #ordered_json_processor,
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


from pathlib import Path
from functools import wraps


def with_location(func):
    filename = Path(func.__code__.co_filename).name
    lineno = func.__code__.co_firstlineno
    func_name = func.__name__

    @wraps(func)
    async def wrapper(*args, **kwargs):
        structlog.contextvars.bind_contextvars(
            filename=filename,
            func_name=func_name,
            lineno=lineno,
        )
        try:
            return await func(*args, **kwargs)
        finally:
            structlog.contextvars.unbind_contextvars("filename", "func_name", "lineno")
    return wrapper
