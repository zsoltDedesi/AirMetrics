from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable

from app.db import Reading, now_ts
from app.sensors.am2302 import AM2302
from app.sensors.ds18b20 import DS18B20


@dataclass(frozen=True)
class Thresholds:
    delta_t: float = 0.02
    delta_rh: float = 0.1


PublishFn = Callable[[dict], Awaitable[None]]
EnqueueFn = Callable[[Reading], None]


class Sampler:
    def __init__(
        self,
        *,
        ds18b20: DS18B20,
        am2302: AM2302,
        interval_seconds: float = 5.0,
        thresholds: Thresholds = Thresholds(),
        publish: PublishFn,
        enqueue: EnqueueFn,
    ) -> None:
        
        self._ds18b20 = ds18b20
        self._am2302 = am2302
        self._interval_seconds = interval_seconds
        self._thresholds = thresholds
        self._publish = publish
        self._enqueue = enqueue

        self._last_ds_temp: float | None = None
        self._last_am_temp: float | None = None
        self._last_am_rh: float | None = None

        self._stop = asyncio.Event()

    def stop(self) -> None:
        self._stop.set()

    async def run(self) -> None:
        while not self._stop.is_set():
            await self._sample_once()
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self._interval_seconds)
            except TimeoutError:
                pass

    async def _sample_once(self) -> None:
        ts = now_ts()

        ds = await asyncio.to_thread(self._ds18b20.read_sensor_temp)
        if ds is not None:
            ds_temp = float(ds["temperature"])
            if self._should_emit_temp(self._last_ds_temp, ds_temp):
                self._last_ds_temp = ds_temp
                reading = Reading(sensor="ds18b20", temperature=ds_temp, humidity=None, ts=ts)
                self._enqueue(reading)
                await self._publish({"sensor": "ds18b20", "temperature": ds_temp, "humidity": None, "ts": ts})

        am = await asyncio.to_thread(self._am2302.read_sensor)
        am_temp = float(am["temperature"])
        am_rh = float(am["humidity"])
        if self._should_emit_temp(self._last_am_temp, am_temp) or self._should_emit_rh(self._last_am_rh, am_rh):
            self._last_am_temp = am_temp
            self._last_am_rh = am_rh
            reading = Reading(sensor="am2302", temperature=am_temp, humidity=am_rh, ts=ts)
            self._enqueue(reading)
            await self._publish({"sensor": "am2302", "temperature": am_temp, "humidity": am_rh, "ts": ts})

    def _should_emit_temp(self, last: float | None, current: float) -> bool:
        if last is None:
            return True
        return abs(current - last) >= self._thresholds.delta_t

    def _should_emit_rh(self, last: float | None, current: float) -> bool:
        if last is None:
            return True
        return abs(current - last) >= self._thresholds.delta_rh
