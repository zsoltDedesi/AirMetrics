# API Contract

## Purpose

This document defines the AirMetrics backend API contract.

Use it when implementing or changing API endpoints, request/response models, validation behavior, authentication expectations, or error formats.

## API Base Path

Main API prefix:

```text
/api
```

Routes intentionally outside the prefix:

| Route | Reason |
| --- | --- |
| none | All current backend routes are mounted under `/api`. |

## Authentication

Status:

- Not implemented.

Rules:

- Treat the API as trusted-network only.
- Do not expose the backend publicly without adding and documenting authentication or network-level protection.
- If authentication is added, update this file, `docs/architecture.md`, `docs/DEPLOYMENT.md`, and `docs/decisions.md`.

## Error Format

FastAPI default `HTTPException` errors are currently used.

Standard error response shape:

```json
{
  "detail": "Human readable message"
}
```

Validation errors from FastAPI/Pydantic may use FastAPI's default structured validation response.

## Shared Models

### Reading

```json
{
  "sensor": "ds18b20",
  "temperature": 22.5,
  "humidity": null,
  "ts": 1710000000
}
```

Fields:

| Field | Type | Required | Notes |
| --- | --- | ---: | --- |
| `sensor` | string | yes | Logical sensor name, currently `ds18b20` or `am2302`. |
| `temperature` | number | yes | Celsius. |
| `humidity` | number or null | no | Relative humidity percentage; present for AM2302 readings. |
| `ts` | integer | yes | Unix timestamp in seconds. |

## Endpoints

### GET /api/health/live

Purpose:

- Liveness check for the HTTP process.

Request:

- No body.

Response:

```json
{
  "ok": true
}
```

Status codes:

| Status | Meaning |
| ---: | --- |
| 200 | Backend process can respond. |

### GET /api/health/ready

Purpose:

- Hardware-aware readiness check for database and sensors.

Request:

- No body.

Response:

```json
{
  "db": true,
  "ds18b20": true,
  "am2302": true
}
```

Status codes:

| Status | Meaning |
| ---: | --- |
| 200 | Readiness check completed. Individual values may be `false`. |

Notes:

- Readiness can be degraded even when liveness is healthy.
- In `SENSOR_MODE=disabled`, sensor readiness values are `false` because no sensor drivers are started.
- In `SENSOR_MODE=degraded`, unavailable sensors report `false` while available sensors can still report `true`.

### GET /api/sensors/{sensor_name}/latest

Purpose:

- Return the latest in-memory reading for one configured sensor.

Path parameters:

| Name | Required | Example | Description |
| --- | ---: | --- | --- |
| `sensor_name` | yes | `ds18b20` | Logical sensor name. |

Response:

```json
{
  "sensor": "ds18b20",
  "temperature": 22.5,
  "humidity": null,
  "ts": 1710000000
}
```

Status codes:

| Status | Meaning |
| ---: | --- |
| 200 | Latest reading exists. |
| 404 | Sensor name is unknown or no reading exists yet. |

### GET /api/history

Purpose:

- Return persisted readings since a parsed timestamp.

Query parameters:

| Name | Required | Default | Example | Description |
| --- | ---: | --- | --- | --- |
| `since` | no | `24h` | `24h`, `30m`, `now-24h`, `1710000000` | Unix timestamp or relative time filter. |

Response:

```json
{
  "readings": [
    {
      "sensor": "ds18b20",
      "temperature": 22.5,
      "humidity": null,
      "ts": 1710000000
    }
  ]
}
```

Status codes:

| Status | Meaning |
| ---: | --- |
| 200 | History query succeeded. |
| 400 | `since` format is invalid. |

Validation:

- Supported relative units are hours (`h`) and minutes (`m`).
- Supported relative forms include `24h`, `30m`, and `now-24h`.
- Numeric strings are treated as Unix timestamps.

### GET /api/system/status

Purpose:

- Return operational metadata that is useful for the dashboard but is not part of readiness.

Request:

- No body.

Response:

```json
{
  "sensor_mode": "hardware",
  "retention_hours": 24,
  "retention_interval_seconds": 3600.0,
  "last_cleanup_ts": 1710000000,
  "last_cleanup_deleted_count": 12
}
```

Fields:

| Field | Type | Required | Notes |
| --- | --- | ---: | --- |
| `sensor_mode` | string | yes | Current sensor runtime mode. |
| `retention_hours` | integer | yes | Configured retention window. |
| `retention_interval_seconds` | number | yes | Configured retention task interval. |
| `last_cleanup_ts` | integer or null | yes | Unix timestamp for the last successful retention cleanup; `null` before the first run. |
| `last_cleanup_deleted_count` | integer or null | yes | Number of rows deleted by the last cleanup; `null` before the first run. |

Status codes:

| Status | Meaning |
| ---: | --- |
| 200 | Status query succeeded. |

### GET /api/stream

Purpose:

- Stream live readings over Server-Sent Events.

Request:

- No body.

Response:

- `Content-Type: text/event-stream`

Events:

```text
event: reading
data: {"sensor":"ds18b20","temperature":22.5,"humidity":null,"ts":1710000000}
```

```text
event: ping
data: {}
```

Status codes:

| Status | Meaning |
| ---: | --- |
| 200 | Stream opened. |

Notes:

- On subscribe, the backend sends latest known readings before new live events.
- Ping events are sent during idle periods.
- Slow subscribers may drop queued events.
