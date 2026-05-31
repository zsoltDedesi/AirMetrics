"""Mock sensor drivers for hardware-free development and demos."""

import math
import time


class MockSensor:
    def __init__(
        self,
        *,
        base_temperature: float,
        temperature_amplitude: float = 0.6,
        humidity: float | None = None,
        humidity_amplitude: float = 3.0,
    ) -> None:
        self.base_temperature = base_temperature
        self.temperature_amplitude = temperature_amplitude
        self.base_humidity = humidity
        self.humidity_amplitude = humidity_amplitude
        self.temperature: float | None = None
        self.measure_timestamp: int | None = None

    def read_sensor(self) -> dict:
        now = time.time()
        self.measure_timestamp = int(now)
        self.temperature = self.base_temperature + math.sin(now / 120) * self.temperature_amplitude
        reading = {
            "temperature": round(self.temperature, 2),
            "ts": self.measure_timestamp,
        }

        if self.base_humidity is not None:
            reading["humidity"] = round(
                self.base_humidity + math.sin(now / 180) * self.humidity_amplitude,
                2,
            )

        return reading

    def sensor_is_connected(self) -> bool:
        return True

    def is_read_healthy(self) -> bool:
        return self.measure_timestamp is not None and (time.time() - self.measure_timestamp) <= 60

    def close(self) -> None:
        return None
