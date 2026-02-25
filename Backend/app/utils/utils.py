"""Utility helpers shared across modules, including parsing relative history time filters."""


import re
import time
from typing import Final
from fastapi import HTTPException


# Precompile the regex for performance. The (?:now-)? part makes the "now-" prefix optional, 
# allowing one regex to handle both cases. Using named groups (?P<name>...) for readability.
SINCE_PATTERN: Final = re.compile(r"^(?:now-)?(?P<amount>\d+)(?P<unit>[hm])$")

# Define a mapping for time units to their corresponding multipliers in seconds.
TIME_MULTIPLIERS: Final[dict[str, int]] = {
    "h": 3600,
    "m": 60,
}

def parse_since(value: str) -> int:
    """
    Parses a time string (unix timestamp, '24h', '30m', 'now-24h') into a unix timestamp.
    """
    raw = value.strip().lower()
    match = SINCE_PATTERN.match(raw)

    if raw.isdigit(): return int(raw)
        
    if match:
        amount = int(match.group("amount"))
        unit = match.group("unit")
        
        # Calculate the time delta in seconds based on the unit and amount.
        delta = amount * TIME_MULTIPLIERS[unit]      
        return int(time.time()) - delta

    
    raise ValueError("Invalid since format. Use unix timestamp, '24h', '30m', or 'now-24h'.")
