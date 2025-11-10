"""
base router for all routes in v1
"""

from fastapi import APIRouter
from app.api.v1.incident import router as incident_router

v1_router = APIRouter(prefix="/v1")


v1_router.include_router(incident_router, prefix="/incident", tags=["incident"])
