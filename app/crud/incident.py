"""круд инцидентов"""

from app.crud.base import BaseDAO
from app.models.incident import Incident
from app.schemas.incident import (
    SchemaIncidentResponse,
    SchemaIncidentCreate,
    SchemaIncidentFilter,
    SchemaIncidentPatch,
)


class IncidentDAO(
    BaseDAO[Incident, SchemaIncidentCreate, SchemaIncidentPatch, SchemaIncidentFilter]
):
    """круд инцидентов"""

    model = Incident
    create_schema = SchemaIncidentCreate
    update_schema = SchemaIncidentPatch
    filter_schema = SchemaIncidentFilter
    pydantic_model = SchemaIncidentResponse
