# Database Documentation

## Purpose

This document describes AirMetrics database ownership, structure, migration rules, seed behavior, persistence flow, and failure expectations.

## Database Ownership

Database ownership model:

- The app owns its SQLite database file.

Explanation:

- The backend creates the schema at startup in `Backend/app/db.py`.
- The deployment owns the local database directory through `DB_PATH`.
- Operators are responsible for preserving `/var/lib/airmetrics` or the configured database path across container updates.

## Connection Model

Connection path:

```text
DB_PATH=/var/lib/airmetrics/airmetrics.db
```

Connection rules:

- Backend opens one `aiosqlite` connection during FastAPI lifespan startup.
- The connection is stored in `app.state.db_conn`.
- WAL mode is enabled with `PRAGMA journal_mode=WAL`.
- `PRAGMA synchronous=NORMAL` is used.
- The connection is closed during application shutdown.

## Migrations

Migration strategy:

- Not yet defined.

Migration command:

```bash
# No migration command is currently configured.
```

Rules:

- Do not make incompatible schema changes without a migration plan.
- Prefer additive schema changes if migration tooling is added later.
- Consider existing Raspberry Pi SQLite files before changing schema initialization.

## Seed Data

Seed strategy:

- Not used.

Seed command:

```bash
# No seed command is currently configured.
```

Rules:

- Sensor data should come from real readings or explicit test fixtures.
- Do not add production seed behavior without documenting it here and in `docs/development.md`.

## Tables and Entities

| Table / Entity | Purpose | Notes |
| --- | --- | --- |
| `readings` | Stores emitted sensor readings. | Created automatically if missing. |

### readings

| Column | Type | Required | Notes |
| --- | --- | ---: | --- |
| `id` | INTEGER | yes | Primary key autoincrement. |
| `sensor` | TEXT | yes | Logical sensor name. |
| `temperature` | REAL | no | Celsius reading. |
| `humidity` | REAL | no | Relative humidity percentage. |
| `ts` | INTEGER | yes | Unix timestamp in seconds. |

## Constraints and Indexes

| Constraint / Index | Purpose |
| --- | --- |
| `PRIMARY KEY (id)` | Unique row identity. |
| `idx_readings_ts` | Supports history filtering by timestamp. |
| `idx_readings_sensor_ts` | Supports sensor/time queries if needed. |

## Persistence Flow

```text
Sampler emits Reading
  -> in-memory deque buffer
  -> count-based flush runs at FLUSH_EVERY_READINGS or flusher wakes every FLUSH_EVERY_SECONDS
  -> Database.insert_many writes batch to SQLite
```

Retention flow:

```text
retention task wakes every RETENTION_INTERVAL_SECONDS
  -> cutoff = now - RETENTION_HOURS
  -> delete readings where ts < cutoff
```

## Failure Behavior

- Settings validation fails startup if `DB_PATH` is missing, not absolute, or its parent is not writable.
- Database connection failures happen during startup and prevent the backend from becoming ready.
- Flusher errors are printed and the background loop continues.
- Buffered readings are removed from memory only after the database insert succeeds.
- Retention errors are printed and the background loop continues.
- `/api/health/ready` reports database readiness through `db`.
- If the process stops before the next flush, buffered readings may be lost.
- If the buffer reaches `BUFFER_MAX_READINGS`, the oldest buffered readings can be dropped by the bounded deque before persistence.
