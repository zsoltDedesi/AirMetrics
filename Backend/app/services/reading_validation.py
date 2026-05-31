"""Sensor reading validation helpers for rejecting impossible hardware values."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SensorLimits:
    min_temperature: float
    max_temperature: float
    min_humidity: float | None = None
    max_humidity: float | None = None


SENSOR_LIMITS: dict[str, SensorLimits] = {
    "ds18b20": SensorLimits(min_temperature=-55.0, max_temperature=125.0),
    "am2302": SensorLimits(
        min_temperature=-40.0,
        max_temperature=80.0,
        min_humidity=0.0,
        max_humidity=100.0,
    ),
}


def validate_sensor_data(sensor_name: str, sensor_data: dict) -> None:
    limits = SENSOR_LIMITS.get(sensor_name)
    if limits is None:
        return

    temperature = sensor_data.get("temperature")
    if not _is_finite_number(temperature):
        raise ValueError(f"{sensor_name} temperature is not finite: {temperature!r}")

    if not limits.min_temperature <= float(temperature) <= limits.max_temperature:
        raise ValueError(
            f"{sensor_name} temperature out of range: {temperature} "
            f"not in {limits.min_temperature}..{limits.max_temperature}"
        )

    humidity = sensor_data.get("humidity")
    if humidity is None:
        return

    if not _is_finite_number(humidity):
        raise ValueError(f"{sensor_name} humidity is not finite: {humidity!r}")

    if limits.min_humidity is None or limits.max_humidity is None:
        return

    if not limits.min_humidity <= float(humidity) <= limits.max_humidity:
        raise ValueError(
            f"{sensor_name} humidity out of range: {humidity} "
            f"not in {limits.min_humidity}..{limits.max_humidity}"
        )


def _is_finite_number(value: object) -> bool:
    return isinstance(value, int | float) and math.isfinite(float(value))
