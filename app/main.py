"""
Точка входа для запуска FastAPI-приложения.

Этот модуль инициализирует приложение FastAPI, добавляет необходимые middleware,
настраивает логирование, подключает маршруты и запускает сервер с помощью Uvicorn.

Пример запуска:
    python -m uvicorn app.main:app --host 0.0.0.0 --port 80
"""

#import logging
#import structlog
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.base_router import v1_router
from app.core.config import settings
#from app.core.structlog_configure import configure_logging
#from app.middleware.middleware_log import logging_middleware


# Подавляем логи Uvicorn (оставляем только ошибки или полностью отключаем)
# if not settings.DEBUG:
#     logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
#     logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
#
#
# configure_logging()
# logger = structlog.get_logger()


app = FastAPI(
    debug=settings.DEBUG,
    title="API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


app.add_middleware(
    SessionMiddleware, secret_key=settings.SESSION_MIDDLEWARE_SECRET_KEY, max_age=3600
)
#app.middleware("http")(logging_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PATCH",
    ],
    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
)


app.include_router(v1_router)


@app.get("/", status_code=200)
def root():
    """health check"""
    return {"message": "System is running"}


# if __name__ == "__main__":
    # granian --interface asgi --host 127.0.0.1 --port 8000 --workers 6 --no-access-log app.main:app
    # import uvicorn
    #
    # uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
