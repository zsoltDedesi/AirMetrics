from fastapi import APIRouter

from .health import router as health_router
from .sensors import router as sensors_router
from .stream import router as stream_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(sensors_router)
api_router.include_router(stream_router)
