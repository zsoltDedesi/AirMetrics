"""AM2302 (DHT22) sensor driver with retries, locking, and calibration offset handling."""


import threading
import time
from typing import Any
# from datetime import datetime

import adafruit_dht
import board


class AM2302:
    def __init__(
        self,
        pin: Any | None = None,
        calibration_offset: float = 1.5,
        *,
        use_pulseio: bool = False,
    ):
        self.pin = pin or board.D6
        self.calibration_offset = calibration_offset

        self._dht = adafruit_dht.DHT22(self.pin, use_pulseio=use_pulseio)
        self._lock = threading.Lock()
        # self._last_read_monotonic: float | None = None
 
        self.temperature: float | None = None
        self.humidity: float | None = None
        self.measure_timestamp: int | None = None

        self.hard_failed: bool = False



    def close(self) -> None:
        self._dht.exit()


    def read_sensor(self, *, retries: int = 2, retry_delay_seconds: float = 0.5) -> dict:
        with self._lock:
            last_error: Exception | None = None

            for attempt_to_read_sensor in range(retries + 1):

                try:
                    temperature = self._dht.temperature
                    humidity = self._dht.humidity

                    if temperature is None or humidity is None:
                        raise RuntimeError("AM2302 read returned None")

                    self.temperature = float(temperature)
                    self.humidity = float(humidity)
                    self.measure_timestamp = int(time.time())
                    self.hard_failed = False

                    return {
                        "temperature": self.temperature - float(self.calibration_offset),
                        "humidity": self.humidity,
                        "ts": self.measure_timestamp,
                    }

                except RuntimeError as exc:
                    last_error = exc

                    if attempt_to_read_sensor < retries:
                        time.sleep(retry_delay_seconds)
                        continue

                    # DHT RuntimeError not necessarily means a hardware failure, but after retries we consider it a hard failure.
                    raise

                except Exception as exc:
                    # Not RuntimeError means something else went wrong, likely a hardware/driver issue, we mark it as hard failure immediately without retries.
                    self.hard_failed = True
                    raise

            raise RuntimeError("AM2302 read failed") from last_error


    def is_read_healthy(self) -> bool:
        if self.measure_timestamp is None:
            return False

        return (time.time() - self.measure_timestamp) <= 60


    def sensor_is_connected(self) -> bool:
        return self._dht is not None and not self.hard_failed
