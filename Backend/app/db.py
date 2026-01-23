from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import aiosqlite


@dataclass(frozen=True)
class Reading:
    sensor: str
    temperature: float | None
    humidity: float | None
    ts: int  # unix epoch seconds


class Database:
    def __init__(self, path: str | Path):
        self._path = str(path)

    async def connect(self) -> aiosqlite.Connection:
        db = await aiosqlite.connect(self._path)
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA synchronous=NORMAL;")
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              sensor TEXT NOT NULL,
              temperature REAL,
              humidity REAL,
              ts INTEGER NOT NULL
            );
            """
        )
        await db.execute("CREATE INDEX IF NOT EXISTS idx_readings_ts ON readings(ts);")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_readings_sensor_ts ON readings(sensor, ts);")
        await db.commit()
        return db

    async def insert_many(self, db: aiosqlite.Connection, readings: list[Reading]) -> None:
        if not readings:
            return
        await db.executemany(
            "INSERT INTO readings(sensor, temperature, humidity, ts) VALUES(?, ?, ?, ?);",
            [(r.sensor, r.temperature, r.humidity, r.ts) for r in readings],
        )
        await db.commit()

    async def delete_older_than(self, db: aiosqlite.Connection, *, cutoff_ts: int) -> int:
        cursor = await db.execute("DELETE FROM readings WHERE ts < ?;", (cutoff_ts,))
        await db.commit()
        return cursor.rowcount

    async def history_since(self, db: aiosqlite.Connection, *, since_ts: int) -> list[dict]:
        cursor = await db.execute(
            """
            SELECT sensor, temperature, humidity, ts
            FROM readings
            WHERE ts >= ?
            ORDER BY ts ASC;
            """,
            (since_ts,),
        )
        rows = await cursor.fetchall()
        return [
            {"sensor": sensor, "temperature": temperature, "humidity": humidity, "ts": ts}
            for (sensor, temperature, humidity, ts) in rows
        ]


def now_ts() -> int:
    return int(time.time())
