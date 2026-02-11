"""History endpoint that returns persisted readings filtered by absolute or relative time."""

from fastapi import APIRouter, Query, Request, HTTPException
from app.utils.utils import parse_since

router = APIRouter()


@router.get("/history")
async def history(
    request: Request,
    since: str = Query(default="24h", description="Unix ts or relative: 24h, 30m, now-24h"),
    ) -> dict:

    db = request.app.state.db
    conn = request.app.state.db_conn

    try:
        since_ts = parse_since(since)

    except ValueError as e:
        return HTTPException(status_code=400, detail=str(e))

    readings = await db.history_since(conn, since_ts=since_ts)
    return {"readings": [reading.model_dump() for reading in readings]}
