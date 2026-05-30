"""Utilities for publishing and formatting Server-Sent Events for live sensor updates."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, AsyncIterator

SUBSCRIBER_QUEUE_SIZE = 100
PING_INTERVAL_SECONDS = 15.0


@dataclass(frozen=True)
class SseEvent:
    event: str
    data: Any


class SseHub:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._subscribers: set[asyncio.Queue[SseEvent]] = set()

    async def subscribe(self) -> asyncio.Queue[SseEvent]:
        queue: asyncio.Queue[SseEvent] = asyncio.Queue(maxsize=SUBSCRIBER_QUEUE_SIZE)
        async with self._lock:
            self._subscribers.add(queue)
        return queue

    async def unsubscribe(self, queue: asyncio.Queue[SseEvent]) -> None:
        async with self._lock:
            self._subscribers.discard(queue)

    async def publish(self, event: str, data: Any) -> None:
        async with self._lock:
            subscribers = list(self._subscribers)

        payload = SseEvent(event=event, data=data)
        for queue in subscribers:
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                pass


def format_sse(event: SseEvent) -> str:
    payload = json.dumps(event.data, separators=(",", ":"))
    return f"event: {event.event}\ndata: {payload}\n\n"


async def sse_iterator(queue: asyncio.Queue[SseEvent]) -> AsyncIterator[str]:
    while True:
        try:
            event = await asyncio.wait_for(queue.get(), timeout=PING_INTERVAL_SECONDS)
            yield format_sse(event)
        except asyncio.TimeoutError:
            yield "event: ping\ndata: {}\n\n"
