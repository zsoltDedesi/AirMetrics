"""Background tasks for periodic buffer flushing and retention cleanup in the database."""

import asyncio
import time
from collections import deque
from typing import Callable

import aiosqlite

from app.db import Database, Reading

CleanupHandler = Callable[[int, int], None]


async def flush_buffer(
    buffer: deque[Reading],
    db: Database,
    db_conn: aiosqlite.Connection,
) -> None:
    if not buffer:
        return

    batch = list(buffer)
    await db.insert_many(db_conn, batch)

    for _ in range(min(len(batch), len(buffer))):
        buffer.popleft()


async def flusher(
    buffer: deque[Reading],
    db: Database,
    db_conn: aiosqlite.Connection,
    interval_seconds: float,
    flush_lock: asyncio.Lock,
) -> None:
    """Periodically flush buffered readings to the database."""

    while True:
        try:
            await asyncio.sleep(interval_seconds)
            async with flush_lock:
                await flush_buffer(buffer, db, db_conn)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Flusher error: {e}")


async def retention(
    db: Database,
    db_conn: aiosqlite.Connection,
    interval_seconds: float = 3600.0,
    retention_hours: int = 24,
    on_cleanup: CleanupHandler | None = None,
) -> None:
    """Periodically delete old readings from the database based on retention policy."""

    while True:
        try:
            await asyncio.sleep(interval_seconds)
            cutoff = int(time.time()) - retention_hours * 3600
            deleted_count = await db.delete_older_than(db_conn, cutoff_ts=cutoff)
            cleanup_ts = int(time.time())

            if on_cleanup is not None:
                on_cleanup(cleanup_ts, deleted_count)

            if deleted_count > 0:
                print(f"Retention: deleted {deleted_count} old readings.")

        except asyncio.CancelledError:
            break

        except Exception as e:
            print(f"Retention error: {e}")
