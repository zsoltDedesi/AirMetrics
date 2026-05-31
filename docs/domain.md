# Domain Model

## Purpose

This document describes the business concepts, domain rules, important states, and terminology used by AirMetrics.

Use this file when implementing features that depend on sensor meaning, sampling behavior, retention rules, or user-visible monitoring behavior.

## Core Concepts

### Sensor

Meaning:

- A physical device connected to the Raspberry Pi that can produce environmental measurements.

Rules:

- `ds18b20` provides temperature readings from Linux 1-Wire sysfs.
- `am2302` provides temperature and relative humidity readings through GPIO.
- AM2302 temperature and relative humidity can be calibrated independently through backend settings.
- Sensors are initialized during backend startup according to `SENSOR_MODE`.
- Sensor readiness is hardware-sensitive and can be false while the HTTP service is alive.
- `hardware` mode requires expected sensors to initialize successfully.
- `degraded` mode starts with any sensors that can initialize.
- `mock` mode uses generated readings for development or demo without hardware.
- `disabled` mode starts without sensor drivers or sampler tasks.

Example:

```text
The DS18B20 device folder is configured as DS18B20_DEVICE_ID=28-000000000000.
```

### Reading

Meaning:

- A single emitted sensor measurement represented by the `Reading` model in `Backend/app/db.py`.

Rules:

- `sensor` is the logical sensor name.
- `temperature` is Celsius.
- `humidity` is optional and represents relative humidity percentage.
- `ts` is a Unix timestamp in seconds.
- Readings are immutable Pydantic models.

Example:

```text
{"sensor":"am2302","temperature":22.4,"humidity":48.2,"ts":1710000000}
```

### Sampling

Meaning:

- The repeated process of reading a sensor driver and deciding whether the value should be emitted.

Rules:

- Each sensor has its own sampling interval.
- Blocking sensor reads run through `asyncio.to_thread`.
- Raw readings are rejected before emission if they are non-finite or outside sensor-specific physical limits.
- AM2302 readings are smoothed with a 5-sample rolling median before emission decisions.
- AM2302 threshold-crossing changes must be confirmed by 2 consecutive median candidates in the same direction.
- The first valid reading is emitted.
- Later readings are emitted only when a configured temperature or humidity threshold is reached.

Example:

```text
If the last DS18B20 reading was 22.0 C and THRESHOLD_DELTA_T_HIGH is 0.125, a new 22.2 C reading is emitted.
```

### Buffer

Meaning:

- A process-local in-memory queue of emitted readings waiting to be persisted.

Rules:

- The buffer size is limited by `BUFFER_MAX_READINGS`.
- Buffered readings are flushed to SQLite when `FLUSH_EVERY_READINGS` is reached or on `FLUSH_EVERY_SECONDS`.
- Buffered readings are removed from memory only after a successful database insert.
- Buffered readings can be lost if the process exits before a flush.

Example:

```text
A reading is sent to SSE immediately, then written to SQLite during the next flush cycle.
```

### History

Meaning:

- Persisted readings queried from SQLite for charting or review.

Rules:

- `/api/history` returns readings at or after the parsed `since` timestamp.
- `since` accepts Unix timestamps and relative values like `24h`, `30m`, and `now-24h`.
- Results are ordered by timestamp ascending.

Example:

```text
GET /api/history?since=24h returns readings from the last 24 hours.
```

### Retention

Meaning:

- Periodic deletion of old persisted readings.

Rules:

- Readings older than `RETENTION_HOURS` are deleted.
- Cleanup runs every `RETENTION_INTERVAL_SECONDS`.

Example:

```text
With RETENTION_HOURS=24, readings older than one day are deleted by the retention task.
```

## Business Rules

| Rule | Description | Source or Reason |
| --- | --- | --- |
| Emit first valid reading | A sampler emits its first valid reading immediately. | Dashboard needs an initial value. |
| Reject impossible readings | Readings outside physical sensor limits are rejected before buffering. | Prevents obvious sensor spikes from polluting stored history. |
| Smooth AM2302 noise | AM2302 uses 5-sample median smoothing and 2-reading confirmation before emitting changed values. | Reduces valid-range DHT22/AM2302 jitter without changing DS18B20 behavior. |
| Emit significant changes only | Later readings require configured temperature or humidity delta. | Reduces storage and stream noise. |
| Persist emitted readings | Emitted readings are buffered and flushed to SQLite. | History charts need persisted data. |
| Retain recent history only | Old readings are deleted according to `RETENTION_HOURS`. | Keeps local SQLite storage bounded. |
| Readiness includes hardware | `/api/health/ready` checks DB and sensors, not only HTTP liveness. | Hardware failures should be visible. |

## Domain Boundaries

| Boundary | Belongs Here | Does Not Belong Here |
| --- | --- | --- |
| Sensor reading | Backend sensor drivers and sampler service. | Frontend components or API route handlers. |
| Significant-change decision | `Backend/app/services/sampler.py`. | Chart components or database queries. |
| History range parsing | Backend utility used by `/api/history`; frontend may calculate display ranges. | Duplicated API validation in UI-only code. |
| Persistence and retention | `Backend/app/db.py` and `Backend/app/services/tasks.py`. | Frontend state or route handlers with ad hoc SQL. |
| Display formatting | Frontend components and chart configuration. | Backend persistence models. |

## Centralized Computed Logic

- Sensor threshold decisions belong in `Backend/app/services/sampler.py`.
- Sensor physical-range validation belongs in `Backend/app/services/reading_validation.py`.
- AM2302 noise filtering belongs in `Backend/app/services/reading_filter.py`.
- History `since` parsing belongs in `Backend/app/utils/utils.py`.
- SQLite schema, inserts, retention deletes, and history queries belong in `Backend/app/db.py`.
- Chart axis and tooltip formatting belongs in frontend chart components.
- Deployment-specific mounts, devices, ports, and image names belong in `Backend/docker-compose.yml`, `Backend/Dockerfile`, and `docs/DEPLOYMENT.md`.

## Important States

| State | Meaning | Allowed Next States | Notes |
| --- | --- | --- | --- |
| service starting | FastAPI lifespan is initializing settings, DB, sensors, and tasks. | running, degraded, failed startup | Startup can fail on invalid config or missing hardware in `hardware` mode. |
| running | Background samplers and API routes are active. | shutting down, degraded | Normal runtime state. |
| degraded | Service responds, but DB or one sensor may be unhealthy or absent by mode. | running, shutting down | Reflected by readiness checks. |
| shutting down | Tasks are cancelled and resources are closed. | stopped | Buffer is flushed when possible. |
| stopped | Process is not serving requests. | service starting | Managed by local process or Docker. |

## Validation Rules

| Field or Action | Rule | Error Handling |
| --- | --- | --- |
| `DB_PATH` | Must be absolute and parent directory must exist, be a directory, and be writable. | Settings validation fails at startup. |
| `SENSOR_MODE` | Must be `hardware`, `degraded`, `mock`, or `disabled`. | Settings validation fails at startup. |
| `DS18B20_DEVICE_ID` | Must be configured in `hardware` mode. | Settings validation fails or sensor init raises not found. |
| DS18B20 read | Device file must exist and report CRC `YES`. | Read returns no emitted reading when invalid. |
| AM2302 read | Temperature and humidity must be non-null after retries. | Runtime errors are logged by sampler. |
| AM2302 humidity calibration | `AM2302_HUMIDITY_CALIBRATION_OFFSET` is added to the raw relative humidity reading before validation, filtering, buffering, and display. | Calibrated value outside `0%..100%` is rejected. |
| DS18B20 emitted range | Temperature must be finite and between `-55 C` and `125 C`. | Reading is logged and rejected before buffering. |
| AM2302 emitted range | Temperature must be finite and between `-40 C` and `80 C`; humidity must be finite and between `0%` and `100%`. | Reading is logged and rejected before buffering. |
| `since` query | Must parse as supported absolute or relative timestamp. | `/api/history` returns HTTP 400. |
| Unknown sensor latest request | Sensor name must exist in app state. | `/api/sensors/{sensor_name}/latest` returns HTTP 404. |

## Domain Events

| Event | Trigger | Result |
| --- | --- | --- |
| `ReadingEmitted` | Sampler receives first valid reading or a filtered threshold change is confirmed. | Reading is buffered and published to SSE subscribers. |
| `BufferFlushed` | Flusher interval runs or `FLUSH_EVERY_READINGS` is reached and buffer has readings. | Readings are inserted into SQLite. |
| `RetentionCleanup` | Retention interval runs. | Old readings are deleted from SQLite and cleanup status is updated for `/api/system/status`. |
| `SseSubscribed` | Client connects to `/api/stream`. | Latest known readings are sent before live events. |

## Terminology

| Term | Meaning |
| --- | --- |
| AirMetrics | The local environmental monitoring project. |
| DS18B20 | 1-Wire temperature sensor. |
| AM2302 | DHT22-compatible temperature and humidity sensor. |
| Reading | Emitted sensor measurement used by API, stream, and database. |
| Sampler | Backend service that polls a sensor and emits significant readings. |
| SSE | Server-Sent Events, used for one-way live backend-to-frontend updates. |
| Retention | Deletion of old persisted readings. |
| Ready | Backend state where DB and sensor checks pass. |
| Live | Backend HTTP process can respond. |
| Sensor mode | Runtime policy deciding whether hardware, partial hardware, mock sensors, or no sensors are started. |
| Median confirmation | AM2302 filter rule requiring a rolling median change to repeat before emission. |

## Open Domain Questions

| Question | Why It Matters | Status |
| --- | --- | --- |
| Should readings also be stored at fixed intervals even without significant change? | Current history shows changes, not a uniform time series. | open |
| What humidity/temperature thresholds are correct for the deployment environment? | Thresholds control storage volume and chart granularity. | open |
| Should degraded sensor state be displayed as a first-class frontend state? | Users may need clear visibility into partial hardware failures. | open |
| Should AM2302 filter settings become configurable? | Current filter constants are intentionally simple but may need field tuning after hardware observation. | open |
