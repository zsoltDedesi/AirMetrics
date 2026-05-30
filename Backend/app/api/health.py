"""Health-check endpoints for liveness and hardware-aware readiness."""

from fastapi import APIRouter, Request

from app.services.health_service import check_db, check_sensors

router = APIRouter()


@router.get("/health/live")
def health() -> dict[str, bool]:
    return {"ok": True}


@router.get("/health/ready")
async def ready(request: Request) -> dict[str, bool]:
    samplers = request.app.state.sampler

    return {
        "db": await check_db(request.app.state.db_conn),
        "ds18b20": _sensor_ready(samplers, "ds18b20"),
        "am2302": _sensor_ready(samplers, "am2302"),
    }


def _sensor_ready(samplers: dict, sensor_name: str) -> bool:
    sampler = samplers.get(sensor_name)
    return check_sensors(sampler.driver) if sampler else False
