"""DS18B20 1-Wire sensor driver for discovery and temperature reads from sysfs."""

import time
from pathlib import Path


class DS18B20NotFoundError(RuntimeError):
    pass


class DS18B20:
    BASE_PATH = Path("/sys/bus/w1/devices")
    BASE_SENSOR_PATTERN = "28-*"

    def __init__(self, device_id: str | None = None):
        self.device_folder = self._find_sensor_folder(device_id)
        self.device_file = self.device_folder / "w1_slave"
        self.temperature: float | None = None

    def _find_sensor_folder(self, device_id: str | None = None) -> Path:
        if device_id:
            path = self.BASE_PATH / device_id
            if not path.exists():
                raise DS18B20NotFoundError(f"DS18B20 device not found: {device_id}")
            return path

        devices = list(self.BASE_PATH.glob(self.BASE_SENSOR_PATTERN))
        if not devices:
            raise DS18B20NotFoundError(f"No DS18B20 devices found under {self.BASE_PATH}")

        return devices[0]

    def read_sensor(self) -> dict | None:
        self.temperature = None

        with open(self.device_file, "r") as sensor_file:
            lines = sensor_file.readlines()

        if len(lines) < 2:
            return None
        if not lines[0].strip().endswith("YES"):
            return None

        _, separator, temp = lines[1].strip().partition("t=")
        if separator != "t=":
            return None

        self.temperature = float(temp) / 1000.0
        return {
            "temperature": self.temperature,
            "ts": int(time.time()),
        }

    def sensor_is_connected(self) -> bool:
        return self.device_file.exists()

    def is_read_healthy(self) -> bool:
        return self.temperature is not None
