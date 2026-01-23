import os
from contextlib import asynccontextmanager
import asyncio
from collections import deque
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse

from app.sensors.am2302 import AM2302
from app.sensors.ds18b20 import DS18B20, DS18B20NotFoundError
from app.db import Database, Reading, now_ts
from app.stream import SseHub, sse_iterator
from app.services.sampler import Sampler, Thresholds



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


@asynccontextmanager
async def lifespan(app: FastAPI):
    sensor_ds18b20 = DS18B20(os.getenv("DS18B20_DEVICE_ID", "DS_SENSOR_ID"))
    sensor_am2302 = AM2302(
        calibration_offset=_get_float_env("AM2302_CALIBRATION_OFFSET", 1.0),
        min_seconds_between_reads=_get_float_env("AM2302_MIN_SECONDS_BETWEEN_READS", 2.0),
    )

    hub = SseHub()
    db = Database(os.getenv("DB_PATH", "DB_PATH"))
    db_conn = await db.connect()

    buffer: deque[Reading] = deque(maxlen=int(_get_float_env("BUFFER_MAX_READINGS", 10_000)))

    def enqueue(reading: Reading) -> None:
        # called from event loop thread
        if len(buffer) == buffer.maxlen:
            # drop oldest; acceptable loss within buffer window
            buffer.popleft()
        buffer.append(reading)

    async def publish(payload: dict) -> None:
        await hub.publish("reading", payload)

    sampler = Sampler(
        ds18b20=sensor_ds18b20,
        am2302=sensor_am2302,
        interval_seconds=_get_float_env("SAMPLE_INTERVAL_SECONDS", 5.0),
        thresholds=Thresholds(
            delta_t=_get_float_env("THRESHOLD_DELTA_T", 0.02),
            delta_rh=_get_float_env("THRESHOLD_DELTA_RH", 0.1),
        ),
        publish=publish,
        enqueue=enqueue,
    )

    async def flusher() -> None:
        flush_every = _get_float_env("FLUSH_EVERY_SECONDS", 300.0)
        while True:
            await asyncio.sleep(flush_every)
            batch = list(buffer)
            buffer.clear()
            await db.insert_many(db_conn, batch)

    async def retention() -> None:
        while True:
            await asyncio.sleep(3600.0)
            cutoff = now_ts() - 24 * 3600
            await db.delete_older_than(db_conn, cutoff_ts=cutoff)

    app.state.sensor_ds18b20 = sensor_ds18b20
    app.state.sensor_am2302 = sensor_am2302
    app.state.hub = hub
    app.state.db = db
    app.state.db_conn = db_conn
    app.state.buffer = buffer
    app.state.sampler = sampler

    sampler_task = asyncio.create_task(sampler.run(), name="sampler")
    flusher_task = asyncio.create_task(flusher(), name="flusher")
    retention_task = asyncio.create_task(retention(), name="retention")

    try:
        yield
    finally:
        sampler.stop()
        sampler_task.cancel()
        flusher_task.cancel()
        retention_task.cancel()
        await asyncio.gather(sampler_task, flusher_task, retention_task, return_exceptions=True)
        batch = list(buffer)
        buffer.clear()
        await db.insert_many(db_conn, batch)
        await db_conn.close()
        sensor_am2302.close()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/sensors/am2302/latest")
def am2302_latest():
    try:
        sensor_am2302: AM2302 = app.state.sensor_am2302
        temp = sensor_am2302.read_sensor_temp()
        if temp is not None:
            return jsonable_encoder(temp)

        raise HTTPException(status_code=503, detail="Failed to read temperature from AM2302 sensor")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # sampler: AM2302Sampler = app.state.am2302_sampler
    # latest = sampler.latest()

    # if latest.value is not None:
    #     return latest.value
    
    # raise HTTPException(status_code=503, detail={"error": latest.error, "updated_at": latest.updated_at})


@app.get("/sensors/ds18b20/latest")
def ds18b20_latest():

    try:
        sensor_ds18b20: DS18B20 = app.state.sensor_ds18b20
        temp = sensor_ds18b20.read_sensor_temp()
        if temp is not None:
            return jsonable_encoder(temp)

        raise HTTPException(status_code=503, detail="Failed to read temperature from DS18B20 sensor")
    
    except DS18B20NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/history")
async def api_history(since: str = Query(default="24h")):
    db: Database = app.state.db
    db_conn = app.state.db_conn
    since_ts = _parse_since(since)
    return await db.history_since(db_conn, since_ts=since_ts)


@app.get("/api/stream")
async def api_stream():
    hub: SseHub = app.state.hub
    queue = await hub.subscribe()
    async def event_gen():
        try:
            async for chunk in sse_iterator(queue):
                yield chunk
        finally:
            await hub.unsubscribe(queue)

    return StreamingResponse(event_gen(), media_type="text/event-stream")
