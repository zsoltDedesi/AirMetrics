"""Health-check endpoint module used for liveness monitoring of the backend service."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}
