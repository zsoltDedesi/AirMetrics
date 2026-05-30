"""Utility helpers shared across modules, including parsing relative history time filters."""

import re
import time
from typing import Final

SINCE_PATTERN: Final = re.compile(r"^(?:now-)?(?P<amount>\d+)(?P<unit>[hm])$")
TIME_MULTIPLIERS: Final[dict[str, int]] = {
    "h": 3600,
    "m": 60,
}


def parse_since(value: str) -> int:
    """Parse unix timestamp or relative time string into a unix timestamp."""
    raw = value.strip().lower()

    if raw.isdigit():
        return int(raw)

    match = SINCE_PATTERN.match(raw)
    if match:
        amount = int(match.group("amount"))
        unit = match.group("unit")
        delta = amount * TIME_MULTIPLIERS[unit]
        return int(time.time()) - delta

    raise ValueError("Invalid since format. Use unix timestamp, '24h', '30m', or 'now-24h'.")
