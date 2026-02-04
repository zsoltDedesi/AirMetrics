# DS18B20 Temperature Sensor Reader

import os, glob
from pathlib import Path
import time
# from datetime import datetime

class DS18B20NotFoundError(RuntimeError):
    pass


class DS18B20:
    BASE_PATH = Path("/sys/bus/w1/devices")
    BASE_SENSOR_PATTERN = "28-*"

    def __init__(self, device_id: str | None = None):
        self.device_folder = self._sensor_is_connected(device_id)
        self.device_file = self.device_folder / "w1_slave"

    def _sensor_is_connected(self, device_id: str | None = None) -> Path:
        """
        Check for connected DS18B20 sensors and return the device path.
        
        :param device_id: Optional device ID to look for.
        :return: Path to the device folder.

        """

        if device_id:
            path = self.BASE_PATH / device_id
            if not path.exists():
                raise DS18B20NotFoundError(f"DS18B20 device not found: {device_id}")
            return path

        if not (devices:=list(self.BASE_PATH.glob(self.BASE_SENSOR_PATTERN))):
            raise DS18B20NotFoundError(f"No DS18B20 devices found under {self.BASE_PATH}")

        return devices[0]


    def read_sensor(self) -> dict | None:
        """
        Read temperature from the DS18B20 sensor.
        :return: Temperature in Celsius, or None if read failed.
        """
        
        with open(self.device_file, 'r') as f:
            lines = f.readlines()
                
        if not lines[0].strip().endswith('YES'):
            return None
    
        temp_line = lines[1].split('t=')[1]
        temp_c = float(temp_line) / 1000.0


        return {"temperature": float(f"{temp_c:.2f}"),
                "ts": int(time.time())
                }

