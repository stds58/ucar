"""классы исключений"""

import logging
from typing import Callable, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


class CustomHTTPException(HTTPException):
    """кастомный класс ошибки"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal server error"
    log_func: Callable = logging.error

    def __init__(self, custom_detail: Optional[str] = None) -> None:
        final_detail = custom_detail if custom_detail is not None else self.detail
        super().__init__(status_code=self.status_code, detail=final_detail)

    async def __call__(self, request: Request, exception: Exception) -> JSONResponse:
        self.log_func("%s: %s", self.detail, exception)
        return JSONResponse(
            content={"message": self.detail},
            status_code=self.status_code,
        )


class CustomInternalServerException(CustomHTTPException):
    """Внутренняя ошибка сервера"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Внутренняя ошибка сервера"
    log_func = logger.error


class IntegrityErrorException(CustomInternalServerException):
    """Нарушение целостности данных"""

    status_code = status.HTTP_409_CONFLICT
    detail = "Нарушение целостности данных"


class ObjectsNotFoundByIDError(CustomInternalServerException):
    """Запрашиваемый объект не найден"""

    status_code = status.HTTP_404_NOT_FOUND
    detail = "Запрашиваемый объект не найден"


class DatabaseConnectionException(CustomHTTPException):
    """Сервис базы данных временно недоступен"""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Сервис базы данных временно недоступен"


class SerializationFailureException(CustomHTTPException):
    """Ошибка сериализации"""

    status_code = status.HTTP_409_CONFLICT
    detail = "Serialization failure (40001), should retry transaction"


class SqlalchemyErrorException(CustomInternalServerException):
    """Ошибка базы данных"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Ошибка базы данных"
