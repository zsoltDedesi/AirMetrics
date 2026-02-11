"""Database models and async SQLite access layer for storing and querying readings."""

import time
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

import aiosqlite


class Reading(BaseModel):
    model_config = ConfigDict(frozen=True) # Make the model immutable
    
    sensor: str
    temperature: float
    humidity: Optional[float] = None
    ts: int = Field(default_factory=lambda: int(time.time()))


class Database:
    def __init__(self, path: str | Path):
        self._path = str(path)
        Path(self._path).parent.mkdir(parents=True, exist_ok=True)

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

    async def history_since(self, db: aiosqlite.Connection, *, since_ts: int) -> list[Reading]:
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
        return [Reading(sensor=s, temperature=t, humidity=h, ts=ts) for (s, t, h, ts) in rows]


def now_ts() -> int:
    return int(time.time())
