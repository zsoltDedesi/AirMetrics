"""
Support utility functions

"""
import os
from datetime import datetime, timezone
from fastapi import HTTPException


def _get_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return float(value)


def _parse_since(since: str) -> int:
    since = since.strip()
    if since.endswith("h") and since[:-1].isdigit():
        hours = int(since[:-1])
        return now_ts() - hours * 3600
    if since.endswith("m") and since[:-1].isdigit():
        minutes = int(since[:-1])
        return now_ts() - minutes * 60
    if since.isdigit():
        return int(since)
    
    try:
        dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid since: {since}") from exc