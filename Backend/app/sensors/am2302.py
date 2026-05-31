"""AM2302 (DHT22) sensor driver with retries, locking, and calibration offset handling."""

import threading
import time
from typing import Any

import adafruit_dht
import board


class AM2302:
    def __init__(
        self,
        pin: Any | None = None,
        calibration_offset: float = 1.5,
        humidity_calibration_offset: float = 0.0,
        *,
        use_pulseio: bool = False,
    ):
        self.pin = pin or board.D6
        self.calibration_offset = calibration_offset
        self.humidity_calibration_offset = humidity_calibration_offset

        self._dht = adafruit_dht.DHT22(self.pin, use_pulseio=use_pulseio)
        self._lock = threading.Lock()

        self.temperature: float | None = None
        self.humidity: float | None = None
        self.measure_timestamp: int | None = None
        self.last_failure_timestamp: int | None = None
        self.last_error: str | None = None
        self.consecutive_failures = 0
        self.hard_failed = False

    def close(self) -> None:
        self._dht.exit()

    def read_sensor(self, *, retries: int = 2, retry_delay_seconds: float = 0.5) -> dict:
        with self._lock:
            last_error: Exception | None = None

            for attempt in range(retries + 1):
                try:
                    return self._read_once()
                except RuntimeError as exc:
                    last_error = exc

                    if attempt < retries:
                        time.sleep(retry_delay_seconds)
                        continue

                    self._record_failure(exc)
                    raise
                except Exception as exc:
                    self._record_failure(exc, hard=True)
                    raise

            raise RuntimeError("AM2302 read failed") from last_error

    def _read_once(self) -> dict:
        temperature = self._dht.temperature
        humidity = self._dht.humidity

        if temperature is None or humidity is None:
            raise RuntimeError("AM2302 read returned None")

        self.temperature = float(temperature)
        self.humidity = float(humidity)
        self.measure_timestamp = int(time.time())
        self.last_error = None
        self.consecutive_failures = 0
        self.hard_failed = False

        return {
            "temperature": self.temperature - float(self.calibration_offset),
            "humidity": self.humidity + float(self.humidity_calibration_offset),
            "ts": self.measure_timestamp,
        }

    def is_read_healthy(self) -> bool:
        if self.measure_timestamp is None:
            return False

        return (time.time() - self.measure_timestamp) <= 60 and self.consecutive_failures < 3

    def sensor_is_connected(self) -> bool:
        return self._dht is not None and not self.hard_failed

    def _record_failure(self, exc: Exception, *, hard: bool = False) -> None:
        self.last_failure_timestamp = int(time.time())
        self.last_error = str(exc)
        self.consecutive_failures += 1
        self.hard_failed = hard
