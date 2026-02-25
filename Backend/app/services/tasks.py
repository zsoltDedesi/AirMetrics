"""Background tasks for periodic buffer flushing and retention cleanup in the database."""

from collections import deque
import asyncio
import time

from app.db import Database, Reading


async def flusher(
        buffer: deque[Reading],
        db: Database,
        interval_seconds: float) -> None:
    """Periodically flush buffered readings to the database.
    
        Args:
            buffer (deque[Reading]): The buffer holding readings to flush.
            db (Database): The database instance to insert readings into.
            interval_seconds (float): How often to flush the buffer in seconds.
    """

    while True:
        try:
            await asyncio.sleep(interval_seconds)
            if not buffer:
                continue

            batch = list(buffer)
            buffer.clear()
            async with db.connection() as conn:
                await db.insert_many(conn, batch)

        except asyncio.CancelledError:
            break

        except Exception as e:
            print(f"Flusher error: {e}")


async def retention(
                    db: Database,
                    interval_seconds: float = 3600.0,
                    retention_hours: int = 24) -> None:
    """Periodically delete old readings from the database based on retention policy.
    
        Args:
            db (Database): The database instance to perform deletions on.
            interval_seconds (float): How often to check for old readings in seconds.
            retention_hours (int): How many hours of data to retain in the database.
    """
    
    while True:
        try: 
            await asyncio.sleep(interval_seconds)
            cutoff = int(time.time()) - retention_hours * 3600
            async with db.connection() as conn:
                deleted_count = await db.delete_older_than(conn, cutoff_ts=cutoff)

            if deleted_count > 0:
                print(f"Retention: deleted {deleted_count} old readings.")

        except asyncio.CancelledError:
            break

        except Exception as e:
            print(f"Retention error: {e}")

        
     
