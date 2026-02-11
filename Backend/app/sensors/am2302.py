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


    def close(self) -> None:
        self._dht.exit()


    def sensor_is_connected(self) -> bool:
        try:
            _ = self._dht.temperature
            _ = self._dht.humidity
            return True
        except RuntimeError:
            return False


    def read_sensor(self, *, retries: int = 2, retry_delay_seconds: float = 0.5) -> dict:
        with self._lock:
            last_error: Exception | None = None

            for attempt_to_read_sensor in range(retries + 1):

                try:
                    temperature = self._dht.temperature
                    humidity = self._dht.humidity

                    if temperature is None or humidity is None:
                        raise RuntimeError("AM2302 read returned None")

                    return {
                        "temperature": float(temperature) - float(self.calibration_offset),
                        "humidity": float(humidity),
                        "ts": int(time.time())
                        }
                
                except RuntimeError as exc:
                    last_error = exc
                    
                    if attempt_to_read_sensor < retries:
                        time.sleep(retry_delay_seconds)
                        continue
                    raise
                    
            raise RuntimeError("AM2302 read failed") from last_error



# dht = adafruit_dht.DHT22(board.D6, use_pulseio=False)

# if __name__ == "__main__":

#     while True:
#         try:
#             t = dht.temperature - 1.5
#             h = dht.humidity
#             print(f"{time.strftime("%H:%M:%S", time.localtime())} Hőmérséklet: {t:.1f} °C, Páratartalom: {h:.1f}%")
        
#         except RuntimeError as e:
#             
#             
#             time.sleep(1)        
#             continue

#         time.sleep(5)
