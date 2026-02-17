"""бизнес логика инцидентов"""

from typing import List
from uuid import UUID
#import structlog
from app.core.async_logger import ainfo, aerror
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.incident import IncidentDAO
from app.schemas.incident import (
    SchemaIncidentResponse,
    SchemaIncidentCreate,
    SchemaIncidentPatch,
    SchemaIncidentFilter,
)


#logger = structlog.get_logger()


async def find_many_incident_orm(
    filters: SchemaIncidentFilter, session: AsyncSession
) -> List[SchemaIncidentResponse]:
    #await ainfo("Get incidents", filters=filters)
    result = await IncidentDAO.find_many_orm(filters=filters, session=session)
    #await ainfo("Geted incidents", filters=filters)
    return result

async def find_many_incident_raw_sql(session: AsyncSession) -> List[dict]:
    result = await IncidentDAO.find_many_raw_sql(session=session)
    return result

async def find_many_incident_native() -> List[dict]:
    result = await IncidentDAO.find_many_native()
    return result

async def find_many_incident_dummy() -> List[dict]:
    result = await IncidentDAO.find_many_dummy()
    return result

async def add_one_incident(
    data: SchemaIncidentCreate, session: AsyncSession
) -> SchemaIncidentResponse:
    #await ainfo("Add incident", filters=data)
    result = await IncidentDAO.add_one(session=session, values=data)
    await session.commit()
    #await ainfo("Added incident", filters=data, commit=True)
    return result


async def update_one_incident(
    data: SchemaIncidentPatch, session: AsyncSession, incident_id: UUID
) -> SchemaIncidentResponse:
    #await ainfo("Update incident", model_id=incident_id, filters=data)
    result = await IncidentDAO.update_one(
        session=session, model_id=incident_id, values=data
    )
    await session.commit()
    #await ainfo("Updated incident", model_id=incident_id, filters=data, commit=True)
    return result
