"""
routers for incident
"""

from uuid import UUID
#import structlog
from app.core.async_logger import ainfo, aerror
from app.core.structlog_configure import with_location
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.incident import (
    SchemaIncidentResponse,
    SchemaIncidentCreate,
    SchemaIncidentPatch,
    SchemaIncidentFilter,
)

from app.services.incident import (
    find_many_incident_orm,
    find_many_incident_raw_sql,
    find_many_incident_native,
    find_many_incident_dummy,
    add_one_incident,
    update_one_incident,
)
from app.dependencies.get_db import connection

from asyncio import Lock
from time import monotonic
from typing import Optional
import orjson


#logger = structlog.get_logger()

# Глобальные переменные на воркер
_incidents_cache = None
_incidents_cache_time = 0
_cache_lock: Optional[Lock] = None
CACHE_TTL = 10.0

router = APIRouter()


@router.get("/router-dummy", summary="Get dummy incidents")
async def dummy():
    return [{"id": i, "name": "test"} for i in range(100)]


@router.get("/native/cache", summary="Get cache incidents")
@with_location
async def get_cache_incidents(
    session: AsyncSession = Depends(connection()),
    filters: SchemaIncidentFilter = Depends(),
):
    global _incidents_cache, _incidents_cache_time, _cache_lock

    now = monotonic()
    if _incidents_cache is not None and (now - _incidents_cache_time) < CACHE_TTL:
        return _incidents_cache

    # Создаём lock при первом обращении (внутри event loop)
    if _cache_lock is None:
        _cache_lock = Lock()

    async with _cache_lock:
        now = monotonic()
        if _incidents_cache is not None and (now - _incidents_cache_time) < CACHE_TTL:
            return _incidents_cache

        _incidents_cache = await find_many_incident_native()
        _incidents_cache_time = monotonic()

    return _incidents_cache


@router.get("/orm", summary="Get incidents")
@with_location
async def get_incidents(
    session: AsyncSession = Depends(connection()),
    filters: SchemaIncidentFilter = Depends(),
):
    """получение всех инцидентов"""
    #await ainfo("Get incidents", filters=filters)
    incident = await find_many_incident_orm(
        filters=filters,
        session=session,
    )
    #await ainfo("Geted incidents", filters=filters)
    return incident


@router.get("/raw_sql", summary="Get incidents")
@with_location
async def get_incidents(
    session: AsyncSession = Depends(connection()),
):
    """получение всех инцидентов"""
    #await ainfo("Get incidents", filters=filters)
    incident_data = await find_many_incident_raw_sql(session=session,)
    #await ainfo("Geted incidents", filters=filters)
    return Response(
        content=orjson.dumps(incident_data),
        media_type="application/json"
    )


@router.get("/native", summary="Get incidents")
@with_location
async def get_incidents():
    """получение всех инцидентов"""
    #await ainfo("Get incidents", filters=filters)
    incident = await find_many_incident_native()
    #await ainfo("Geted incidents", filters=filters)
    return incident

@router.get("/native-orjson", summary="Get incidents")
@with_location
async def get_incidents():
    """получение всех инцидентов"""
    incident_data = await find_many_incident_native()
    return Response(
        content=orjson.dumps(incident_data),
        media_type="application/json"
    )

@router.get("/dummy", summary="Get incidents")
@with_location
async def get_incidents():
    """получение всех инцидентов"""
    incident = await find_many_incident_dummy()
    return incident


@router.post("", summary="Create incident")
async def create_incident(
    data: SchemaIncidentCreate,
    session: AsyncSession = Depends(connection()),
):
    """добавить новый инцидент"""
    #await ainfo("Add incident", data=data)
    incident = await add_one_incident(
        data=data,
        session=session,
    )
    #await ainfo("Added incident", data=data)
    return incident


@router.patch(
    "/{incident_id}", summary="Update incident", response_model=SchemaIncidentResponse
)
async def edit_incident(
    incident_id: UUID,
    data: SchemaIncidentPatch,
    session: AsyncSession = Depends(connection()),
):
    """поменять статус инцидента"""
    #logger.info("Update incident", data=data, model_id=incident_id)
    updated_incident = await update_one_incident(
        data=data,
        session=session,
        incident_id=incident_id,
    )
    #logger.info("Updated incident", data=data, model_id=incident_id)
    return updated_incident
