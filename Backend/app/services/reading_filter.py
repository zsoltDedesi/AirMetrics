"""Reading filters for sensor-specific noise reduction before emission."""

from collections import deque
from statistics import median
from typing import Protocol, TypeVar


class FilterableReading(Protocol):
    sensor: str
    temperature: float
    humidity: float | None
    ts: int


ReadingT = TypeVar("ReadingT", bound=FilterableReading)


class MedianConfirmationFilter:
    """Smooth readings with a rolling median and confirm sustained changes."""

    def __init__(self, *, window_size: int, confirmation_readings: int) -> None:
        if window_size <= 0:
            raise ValueError("window_size must be greater than zero")
        if confirmation_readings <= 0:
            raise ValueError("confirmation_readings must be greater than zero")

        self.window_size = window_size
        self.confirmation_readings = confirmation_readings
        self._window: deque[FilterableReading] = deque(maxlen=window_size)
        self._pending_key: tuple[int, int] | None = None
        self._pending_count = 0

    def process(
        self,
        reading: ReadingT,
        *,
        last_emitted: FilterableReading | None,
        threshold_temp: float,
        threshold_humidity: float | None,
    ) -> ReadingT | None:
        self._window.append(reading)
        candidate = self._median_reading(reading)

        if last_emitted is None:
            self._reset_pending()
            return candidate

        key = self._change_key(
            candidate,
            last_emitted=last_emitted,
            threshold_temp=threshold_temp,
            threshold_humidity=threshold_humidity,
        )
        if key == (0, 0):
            self._reset_pending()
            return candidate

        if key == self._pending_key:
            self._pending_count += 1
        else:
            self._pending_key = key
            self._pending_count = 1

        if self._pending_count < self.confirmation_readings:
            return None

        self._reset_pending()
        return candidate

    def _median_reading(self, reading: ReadingT) -> ReadingT:
        temperatures = [item.temperature for item in self._window]
        humidities = [item.humidity for item in self._window if item.humidity is not None]

        return reading.__class__(
            sensor=reading.sensor,
            temperature=float(median(temperatures)),
            humidity=float(median(humidities)) if humidities else None,
            ts=reading.ts,
        )

    def _change_key(
        self,
        candidate: FilterableReading,
        *,
        last_emitted: FilterableReading,
        threshold_temp: float,
        threshold_humidity: float | None,
    ) -> tuple[int, int]:
        temperature_direction = _direction(
            candidate.temperature - last_emitted.temperature,
            threshold_temp,
        )
        humidity_direction = 0
        if (
            threshold_humidity is not None
            and candidate.humidity is not None
            and last_emitted.humidity is not None
        ):
            humidity_direction = _direction(
                candidate.humidity - last_emitted.humidity,
                threshold_humidity,
            )

        return temperature_direction, humidity_direction

    def _reset_pending(self) -> None:
        self._pending_key = None
        self._pending_count = 0


def _direction(delta: float, threshold: float) -> int:
    if delta == 0 or abs(delta) < threshold:
        return 0

    return 1 if delta > 0 else -1
