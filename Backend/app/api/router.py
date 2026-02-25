"""Root API router that composes health, sensor, stream, and history endpoints."""


from fastapi import APIRouter

from .health import router as health_router
from .sensors import router as sensors_router
from .stream import router as stream_router
from .history import router as history_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(sensors_router)
api_router.include_router(stream_router)
api_router.include_router(history_router)
