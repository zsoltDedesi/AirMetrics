"""Sampler service for AirMetrics backend."""

import asyncio

from typing import Awaitable, Callable, Protocol

from app.db import Reading


class SensorDriver(Protocol):
    """Anything that has read_sensor method and returns a dict or None."""
    def read_sensor(self) -> dict | None: ...


class Sampler:
    def __init__(
        self,
        *,
        driver: SensorDriver,
        sensor_name: str,
        treshold_temp: float,
        treshold_humidity: float | None = None,
        interval_seconds: float,
        on_change: Callable[[Reading], Awaitable[None]],
    ):
        self.driver = driver
        self.sensor_name = sensor_name
        self.treshold_temp = treshold_temp
        self.treshold_humidity = treshold_humidity
        self.interval_seconds = interval_seconds
        self.on_change = on_change

        self._last: Reading | None = None
        self._stop = asyncio.Event()


    async def _sample_once(self) -> None:
        # Read from the sensor in a thread to avoid blocking the event loop
        try:
            raw_sensor_data = await asyncio.to_thread(self.driver.read_sensor)
        except Exception as e:
            print(f"Error reading sensor {self.sensor_name}: {e}")
            return

        if raw_sensor_data is None: return

        try:
            current = Reading(sensor=self.sensor_name, **raw_sensor_data)

        except RuntimeError as e:
            print(f"Runtime error for {self.sensor_name}: {e}")
            return

        except Exception as e:
            print(f"Validation error for {self.sensor_name}: {e}")
            return
            
        if self._should_emit(current):
            self._last = current
            await self.on_change(current)
    

    def _should_emit(self, current: Reading) -> bool:
        if self._last is None:
            return True
        
        # Tempterature difference check (absolute value)
        temperature_delta = abs(current.temperature - self._last.temperature) >= self.treshold_temp

        # Humidity difference check (absolute value)
        humidity_delta = False
        if self.treshold_humidity is not None and \
           current.humidity is not None and \
           self._last.humidity is not None:

            if abs(current.humidity - self._last.humidity) >= self.treshold_humidity:
                return True

        return temperature_delta or humidity_delta


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

