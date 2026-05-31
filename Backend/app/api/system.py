"""System status endpoints for dashboard operational metadata."""

from fastapi import APIRouter, Request

from app.services.env_loader import settings

router = APIRouter()


@router.get("/system/status")
def system_status(request: Request) -> dict[str, int | float | str | None]:
    runtime_status = getattr(request.app.state, "runtime_status", {})

    return {
        "sensor_mode": settings.SENSOR_MODE,
        "retention_hours": settings.RETENTION_HOURS,
        "retention_interval_seconds": settings.RETENTION_INTERVAL_SECONDS,
        "last_cleanup_ts": runtime_status.get("last_cleanup_ts"),
        "last_cleanup_deleted_count": runtime_status.get("last_cleanup_deleted_count"),
    }
