"""Asynchronous sampling service that emits readings when change thresholds are exceeded."""

import asyncio
from typing import Awaitable, Callable, Protocol

from pydantic_core import ValidationError

from app.db import Reading
from app.services.reading_validation import validate_sensor_data

ReadingHandler = Callable[[Reading], Awaitable[None]]


class SensorDriver(Protocol):
    """Sensor driver interface used by the sampler."""

    def read_sensor(self) -> dict | None: ...


class Sampler:
    def __init__(
        self,
        *,
        driver: SensorDriver,
        sensor_name: str,
        threshold_temp: float,
        threshold_humidity: float | None = None,
        interval_seconds: float,
        on_change: ReadingHandler,
    ):
        self.driver = driver
        self.sensor_name = sensor_name
        self.threshold_temp = threshold_temp
        self.threshold_humidity = threshold_humidity
        self.interval_seconds = interval_seconds
        self.on_change = on_change

        self._last: Reading | None = None
        self._stop = asyncio.Event()

    async def _sample_once(self) -> None:
        try:
            raw_sensor_data = await asyncio.to_thread(self.driver.read_sensor)
        except Exception as e:
            print(f"Error reading sensor {self.sensor_name}: {e}")
            return

        if raw_sensor_data is None:
            return

        try:
            validate_sensor_data(self.sensor_name, raw_sensor_data)
        except ValueError as e:
            print(f"Invalid reading for {self.sensor_name}: {e}")
            return

        try:
            current = Reading(sensor=self.sensor_name, **raw_sensor_data)
        except ValidationError as e:
            print(f"Validation error for {self.sensor_name}: {e}")
            return
        except Exception as e:
            print(f"Unexpected error processing reading for {self.sensor_name}: {e}")
            return

        if not self._should_emit(current):
            return

        self._last = current
        try:
            await self.on_change(current)
        except Exception as e:
            print(f"Error in on_change for {self.sensor_name}: {e}")

    def _should_emit(self, current: Reading) -> bool:
        if self._last is None:
            return True

        return self._temperature_changed(current) or self._humidity_changed(current)

    def _temperature_changed(self, current: Reading) -> bool:
        if self._last is None:
            return True

        return abs(current.temperature - self._last.temperature) >= self.threshold_temp

    def _humidity_changed(self, current: Reading) -> bool:
        if (
            self._last is None
            or self.threshold_humidity is None
            or current.humidity is None
            or self._last.humidity is None
        ):
            return False

        return abs(current.humidity - self._last.humidity) >= self.threshold_humidity

    async def run(self) -> None:
        while not self._stop.is_set():
            await self._sample_once()
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.interval_seconds)
            except asyncio.TimeoutError:
                continue

    def stop(self) -> None:
        self._stop.set()

    @property
    def last_reading(self) -> Reading | None:
        return self._last
