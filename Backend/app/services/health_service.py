
from typing import Protocol, runtime_checkable
from app.db import Database


@runtime_checkable
class SensorReader(Protocol):
    def sensor_is_connected(self) -> bool: ...

    def is_read_healthy(self) -> bool: ...


def check_sensors(sensor: SensorReader) -> bool:
    return sensor.sensor_is_connected() and sensor.is_read_healthy()


async def check_db(db: Database) -> bool:
    try:
        async with db.connection() as conn:
            await conn.execute("SELECT 1;")
        return True
    except Exception:
        return False

