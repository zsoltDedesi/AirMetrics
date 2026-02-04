
from contextlib import asynccontextmanager
import asyncio
from collections import deque
# from datetime import datetime, timedelta, timezone


from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from app.sensors.am2302 import AM2302
from app.sensors.ds18b20 import DS18B20
from app.db import Database, Reading
from app.stream import SseHub, SseEvent, format_sse, sse_iterator

from app.services.sampler import Sampler
from app.services.tasks import flusher, retention
from app.services.env_loader import settings 



@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Database(settings.DB_PATH)
    db_conn = await db.connect()
    hub = SseHub()
    buffer: deque[Reading] = deque(maxlen=int(settings.BUFFER_MAX_READINGS))

    sensor_ds18b20 = DS18B20(settings.DS18B20_DEVICE_ID)
    sensor_am2302 = AM2302(calibration_offset=settings.AM2302_CALIBRATION_OFFSET)

    def enqueue(reading: Reading) -> None:
        # Enqueue reading to buffer
        buffer.append(reading)

    async def on_reading_change(reading: Reading) -> None:
        enqueue(reading)
        await hub.publish("reading", reading.model_dump())


    samplers = [
        Sampler(
            driver=sensor_ds18b20,
            sensor_name="ds18b20",
            treshold_temp=settings.THRESHOLD_DELTA_T_HIGH,
            interval_seconds=settings.DS18B20_SAMPLING_INTERVAL_SECONDS,
            on_change= on_reading_change),
        Sampler(driver=sensor_am2302,
                sensor_name="am2302",
                treshold_temp=settings.THRESHOLD_DELTA_T_LOW,
                treshold_humidity=settings.THRESHOLD_DELTA_RH,
                interval_seconds=settings.AM2302_SAMPLING_INTERVAL_SECONDS,
                on_change=on_reading_change)
        ]


    tasks = [
        asyncio.create_task(flusher(buffer, db, db_conn, settings.FLUSH_EVERY_SECONDS), name="flusher"),
        asyncio.create_task(retention(db, db_conn, settings.RETENTION_INTERVAL_SECONDS, settings.RETENTION_HOURS), name="retention"),
        *[asyncio.create_task(s.run(), name=f"sampler_{s.sensor_name}") for s in samplers]
    ]

    app.state.hub = hub    
    app.state.sampler = {s.sensor_name: s for s in samplers}
    app.state.db_conn = db_conn
    app.state.db = db

    try:
        yield

    finally:
        # Clean stop
        for s in samplers: s.stop()
        for t in tasks: t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

        if buffer:
            await db.insert_many(db_conn, list(buffer))
        await db_conn.close()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"ok": True}



@app.get("/sensors/{sensor_name}/latest")
async def get_latest(sensor_name):
    samplers = app.state.sampler
    if sensor_name not in samplers:
        raise HTTPException(status_code=404, detail=f"Sensor '{sensor_name}' not found")
    
    latest = samplers[sensor_name].last_reading
    if latest is None:
        raise HTTPException(status_code=404, detail=f"No readings for sensor '{sensor_name}' yet")
    
    return latest


@app.get("/api/stream")
async def api_stream():
    hub: SseHub = app.state.hub
    queue = await hub.subscribe()

    async def event_gen():
        try:
            # Send a snapshot on first subscribe
            for sampler in app.state.sampler.values():
                latest = sampler.last_reading
                if latest is not None:
                    yield format_sse(SseEvent(event="reading", data=latest.model_dump()))

            async for chunk in sse_iterator(queue):
                yield chunk
        finally:
            await hub.unsubscribe(queue)

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # in case of nginx reverse proxy, disable response buffering
    }

    return StreamingResponse(event_gen(), media_type="text/event-stream", headers=headers)
