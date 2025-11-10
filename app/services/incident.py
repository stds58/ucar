"""бизнес логика инцидентов"""

from typing import List
from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.incident import IncidentDAO
from app.schemas.incident import (
    SchemaIncidentResponse,
    SchemaIncidentCreate,
    SchemaIncidentPatch,
    SchemaIncidentFilter,
)


logger = structlog.get_logger()


async def find_many_incident(
    filters: SchemaIncidentFilter, session: AsyncSession
) -> List[SchemaIncidentResponse]:
    logger.info("Get incidents", filters=filters)
    result = await IncidentDAO.find_many(filters=filters, session=session)
    logger.info("Geted incidents", filters=filters)
    return result


async def add_one_incident(
    data: SchemaIncidentCreate, session: AsyncSession
) -> SchemaIncidentResponse:
    logger.info("Add incident", filters=data)
    result = await IncidentDAO.add_one(session=session, values=data)
    await session.commit()
    logger.info("Added incident", filters=data, commit=True)
    return result


async def update_one_incident(
    data: SchemaIncidentPatch, session: AsyncSession, incident_id: UUID
) -> SchemaIncidentResponse:
    logger.info("Update incident", model_id=incident_id, filters=data)
    result = await IncidentDAO.update_one(
        session=session, model_id=incident_id, values=data
    )
    await session.commit()
    logger.info("Updated incident", model_id=incident_id, filters=data, commit=True)
    return result
