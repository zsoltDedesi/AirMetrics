"""Application entrypoint that wires sensors, services, database, and API routes."""

import asyncio
from collections import deque
from contextlib import asynccontextmanager
from typing import Awaitable, Callable, Protocol

import aiosqlite
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.db import Database, Reading
from app.sensors.mock import MockSensor
from app.services.env_loader import settings
from app.services.sampler import Sampler
from app.services.tasks import flush_buffer, flusher, retention
from app.stream import SseHub

ReadingHandler = Callable[[Reading], Awaitable[None]]


class ManagedSensor(Protocol):
    def read_sensor(self) -> dict | None: ...

    def sensor_is_connected(self) -> bool: ...

    def is_read_healthy(self) -> bool: ...


def create_samplers(
    *,
    sensors: dict[str, ManagedSensor],
    on_reading_change: ReadingHandler,
) -> list[Sampler]:
    samplers: list[Sampler] = []

    if "ds18b20" in sensors:
        samplers.append(
            Sampler(
                driver=sensors["ds18b20"],
                sensor_name="ds18b20",
                threshold_temp=settings.THRESHOLD_DELTA_T_HIGH,
                interval_seconds=settings.DS18B20_SAMPLING_INTERVAL_SECONDS,
                on_change=on_reading_change,
            )
        )

    if "am2302" in sensors:
        samplers.append(
            Sampler(
                driver=sensors["am2302"],
                sensor_name="am2302",
                threshold_temp=settings.THRESHOLD_DELTA_T_LOW,
                threshold_humidity=settings.THRESHOLD_DELTA_RH,
                interval_seconds=settings.AM2302_SAMPLING_INTERVAL_SECONDS,
                on_change=on_reading_change,
            )
        )

    return samplers


def create_sensor_drivers() -> dict[str, ManagedSensor]:
    if settings.SENSOR_MODE == "disabled":
        print("Sensor mode disabled: no sensor drivers or samplers will be started.")
        return {}

    if settings.SENSOR_MODE == "mock":
        print("Sensor mode mock: using generated sensor readings.")
        return {
            "ds18b20": MockSensor(base_temperature=23.5, temperature_amplitude=0.4),
            "am2302": MockSensor(
                base_temperature=23.0,
                temperature_amplitude=0.8,
                humidity=55.0,
                humidity_amplitude=4.0,
            ),
        }

    if settings.SENSOR_MODE == "hardware":
        return {
            "ds18b20": _create_ds18b20(),
            "am2302": _create_am2302(),
        }

    sensors: dict[str, ManagedSensor] = {}
    for sensor_name, factory in (
        ("ds18b20", _create_ds18b20),
        ("am2302", _create_am2302),
    ):
        try:
            sensors[sensor_name] = factory()
        except Exception as exc:
            print(f"Sensor mode degraded: {sensor_name} unavailable: {exc}")

    return sensors


def _create_ds18b20() -> ManagedSensor:
    from app.sensors.ds18b20 import DS18B20

    return DS18B20(settings.DS18B20_DEVICE_ID)


def _create_am2302() -> ManagedSensor:
    from app.sensors.am2302 import AM2302

    return AM2302(calibration_offset=settings.AM2302_CALIBRATION_OFFSET)


def create_background_tasks(
    *,
    samplers: list[Sampler],
    buffer: deque[Reading],
    db: Database,
    db_conn: aiosqlite.Connection,
    flush_lock: asyncio.Lock,
) -> list[asyncio.Task]:
    tasks = [
        asyncio.create_task(
            flusher(buffer, db, db_conn, settings.FLUSH_EVERY_SECONDS, flush_lock),
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

    for task in tasks:
        task.add_done_callback(_log_task_result)

    return tasks


def _log_task_result(task: asyncio.Task) -> None:
    if task.cancelled():
        return

    exception = task.exception()
    if exception is not None:
        print(f"Background task {task.get_name()} stopped with error: {exception}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Database(settings.DB_PATH)
    db_conn = await db.connect()
    hub = SseHub()
    buffer: deque[Reading] = deque(maxlen=int(settings.BUFFER_MAX_READINGS))
    flush_lock = asyncio.Lock()
    sensors = create_sensor_drivers()

    async def on_reading_change(reading: Reading) -> None:
        async with flush_lock:
            if buffer.maxlen is not None and len(buffer) == buffer.maxlen:
                print("Reading buffer full: dropping oldest buffered reading.")

            buffer.append(reading)

            if len(buffer) >= settings.FLUSH_EVERY_READINGS:
                try:
                    await flush_buffer(buffer, db, db_conn)
                except Exception as exc:
                    print(f"Count-based buffer flush failed: {exc}")

        await hub.publish("reading", reading.model_dump())

    samplers = create_samplers(
        sensors=sensors,
        on_reading_change=on_reading_change,
    )
    tasks = create_background_tasks(
        samplers=samplers,
        buffer=buffer,
        db=db,
        db_conn=db_conn,
        flush_lock=flush_lock,
    )

    app.state.hub = hub
    app.state.sampler = {sampler.sensor_name: sampler for sampler in samplers}
    app.state.sensor_mode = settings.SENSOR_MODE
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

        try:
            async with flush_lock:
                await flush_buffer(buffer, db, db_conn)
        except Exception as exc:
            print(f"Shutdown buffer flush failed: {exc}")
        finally:
            await db_conn.close()

            for sensor in sensors.values():
                close = getattr(sensor, "close", None)
                if close is not None:
                    close()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
