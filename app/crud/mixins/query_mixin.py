from typing import Optional
from sqlalchemy import and_, Select
from sqlalchemy.orm import DeclarativeBase
from app.crud.mixins.types import FilterSchemaType


class QueryMixin:
    model: type[DeclarativeBase]
    _exclude_from_filter_by: set[str] = set()

    @classmethod
    def _apply_filters(cls, query, filters: FilterSchemaType):
        """игнорирование полей фильтрации, которых нет в модели с поддержкой списков"""
        allowed_fields = cls.filter_schema.model_fields.keys()
        exclude_fields = getattr(cls, "_exclude_from_filter_by", set())

        filter_dict = {
            key: value
            for key, value in filters.model_dump().items()
            if key in allowed_fields and key not in exclude_fields and value is not None
        }

        filters_result = []
        for key, value in filter_dict.items():
            if hasattr(cls.model, key):
                field = getattr(cls.model, key)

                # Если значение - список, используем IN
                if isinstance(value, list):
                    if value:  # Проверяем, что список не пустой
                        filters_result.append(field.in_(value))
                else:
                    # Одиночное значение
                    filters_result.append(field == value)

        if filters_result:
            query = query.filter(and_(*filters_result))
        return query

    @classmethod
    def _build_query(
        cls,
        query: Select,
        filters: Optional[FilterSchemaType] = None,
    ) -> Select:
        if filters is not None:
            query = cls._apply_filters(query, filters)

        return query
