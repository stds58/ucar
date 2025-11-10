"""пидантик схемы инцидентов"""

from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.core.enums import SourceDomain, StatusDomain


class SchemaIncidentResponse(BaseModel):
    id: UUID
    description: str
    status: StatusDomain
    source: SourceDomain
    created_at: datetime
    updated_at: datetime


class SchemaIncidentCreate(BaseModel):
    description: str
    status: StatusDomain
    source: SourceDomain


class SchemaIncidentFilter(BaseModel):
    status: Optional[StatusDomain] = None


class SchemaIncidentPatch(BaseModel):
    description: Optional[str] = None
    status: Optional[StatusDomain] = None
    source: Optional[SourceDomain] = None
