"""Health-check endpoint module used for liveness monitoring of the backend service."""

from fastapi import APIRouter, Request
from app.services.health_service import check_db, check_sensors


router = APIRouter()


@router.get("/health/live")
def health() -> dict[str, bool]:
    return {"ok": True}


@router.get("/health/ready")
async def ready(request: Request) -> dict[str, bool]:
    sampler = request.app.state.sampler
    db = request.app.state.db

    return {"db": await check_db(db),
            "ds18b20": check_sensors(sampler["ds18b20"].driver) if "ds18b20" in sampler else False,
            "am2302": check_sensors(sampler["am2302"].driver) if "am2302" in sampler else False
            }
