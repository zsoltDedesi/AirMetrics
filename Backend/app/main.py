"""Application entrypoint that wires sensors, services, database, and API routes."""

import asyncio
from collections import deque
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

import aiosqlite
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.db import Database, Reading
from app.sensors.am2302 import AM2302
from app.sensors.ds18b20 import DS18B20
from app.services.env_loader import settings
from app.services.sampler import Sampler
from app.services.tasks import flush_buffer, flusher, retention
from app.stream import SseHub

ReadingHandler = Callable[[Reading], Awaitable[None]]


def create_samplers(
    *,
    sensor_ds18b20: DS18B20,
    sensor_am2302: AM2302,
    on_reading_change: ReadingHandler,
) -> list[Sampler]:
    return [
        Sampler(
            driver=sensor_ds18b20,
            sensor_name="ds18b20",
            threshold_temp=settings.THRESHOLD_DELTA_T_HIGH,
            interval_seconds=settings.DS18B20_SAMPLING_INTERVAL_SECONDS,
            on_change=on_reading_change,
        ),
        Sampler(
            driver=sensor_am2302,
            sensor_name="am2302",
            threshold_temp=settings.THRESHOLD_DELTA_T_LOW,
            threshold_humidity=settings.THRESHOLD_DELTA_RH,
            interval_seconds=settings.AM2302_SAMPLING_INTERVAL_SECONDS,
            on_change=on_reading_change,
        ),
    ]


def create_background_tasks(
    *,
    samplers: list[Sampler],
    buffer: deque[Reading],
    db: Database,
    db_conn: aiosqlite.Connection,
) -> list[asyncio.Task]:
    return [
        asyncio.create_task(
            flusher(buffer, db, db_conn, settings.FLUSH_EVERY_SECONDS),
            name="flusher",
        ),
        asyncio.create_task(
            retention(
                db,
                db_conn,
                settings.RETENTION_INTERVAL_SECONDS,
                settings.RETENTION_HOURS,
            ),
            name="retention",
        ),
        *[
            asyncio.create_task(sampler.run(), name=f"sampler_{sampler.sensor_name}")
            for sampler in samplers
        ],
    ]


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Database(settings.DB_PATH)
    db_conn = await db.connect()
    hub = SseHub()
    buffer: deque[Reading] = deque(maxlen=int(settings.BUFFER_MAX_READINGS))

    sensor_ds18b20 = DS18B20(settings.DS18B20_DEVICE_ID)
    sensor_am2302 = AM2302(calibration_offset=settings.AM2302_CALIBRATION_OFFSET)

    async def on_reading_change(reading: Reading) -> None:
        buffer.append(reading)
        await hub.publish("reading", reading.model_dump())

    samplers = create_samplers(
        sensor_ds18b20=sensor_ds18b20,
        sensor_am2302=sensor_am2302,
        on_reading_change=on_reading_change,
    )
    tasks = create_background_tasks(
        samplers=samplers,
        buffer=buffer,
        db=db,
        db_conn=db_conn,
    )

    app.state.hub = hub
    app.state.sampler = {sampler.sensor_name: sampler for sampler in samplers}
    app.state.db_conn = db_conn
    app.state.db = db

    try:
        yield
    finally:
        for sampler in samplers:
            sampler.stop()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

        await flush_buffer(buffer, db, db_conn)
        await db_conn.close()
        sensor_am2302.close()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
