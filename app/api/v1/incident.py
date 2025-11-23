"""
routers for incident
"""

from uuid import UUID
#import structlog
from app.core.async_logger import ainfo, aerror
from app.core.structlog_configure import with_location
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.incident import (
    SchemaIncidentResponse,
    SchemaIncidentCreate,
    SchemaIncidentPatch,
    SchemaIncidentFilter,
)

from app.services.incident import (
    find_many_incident,
    add_one_incident,
    update_one_incident,
)
from app.dependencies.get_db import connection


#logger = structlog.get_logger()


router = APIRouter()


@router.get("", summary="Get incidents")
@with_location
async def get_incidents(
    session: AsyncSession = Depends(connection()),
    filters: SchemaIncidentFilter = Depends(),
):
    """получение всех инцидентов"""
    #await ainfo("Get incidents", filters=filters)
    incident = await find_many_incident(
        filters=filters,
        session=session,
    )
    #await ainfo("Geted incidents", filters=filters)
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
