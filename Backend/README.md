# AirMetrics Backend (FastAPI)

FastAPI service that samples sensors, buffers readings, persists them to SQLite, and exposes an HTTP API (including Server‑Sent Events).

## Requirements

- Raspberry Pi host recommended (GPIO + 1‑Wire).
- DS18B20 via Linux sysfs at `/sys/bus/w1/devices` (1‑Wire).
- AM2302/DHT22 via GPIO (Blinka/Adafruit libraries).

This backend currently expects the sensors to be present at startup. If the hardware or device paths are missing, the service may fail during initialization.

## Configuration (`airmetrics.env`)

The backend loads settings from `Backend/airmetrics.env` (required). Create it from the example:

```bash
cp airmetrics.env.example airmetrics.env
```

Common settings:

- `DB_PATH` (required): absolute path to the SQLite DB file (directory must exist and be writable). Docker setup uses `/var/lib/airmetrics/airmetrics.db`.
- `DS18B20_DEVICE_ID` (required): folder name under `/sys/bus/w1/devices` (typically `28-...`).
- Sampling/threshold/retention settings: see `airmetrics.env.example`.

## Run with Docker (recommended on Raspberry Pi)

```bash
docker compose up --build -d
```

Notes:

- `docker-compose.yml` mounts `./airmetrics.env` into the container at `/app/airmetrics.env`.
- Persisted data is stored under `/var/lib/airmetrics` on the host and mounted into the container.
- Device paths are mounted for 1‑Wire and GPIO access.

## Run locally (without Docker)

From `Backend/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You still need `airmetrics.env` present, and the expected sensor device paths available on your machine.

## API

Base prefix: `/api`

- `GET /api/health/live` — liveness check (`{"ok": true}`).
- `GET /api/health/ready` — readiness: DB + sensor connectivity/health flags.
- `GET /api/sensors/{sensor_name}/latest` — latest in‑memory reading for a sensor (`ds18b20`, `am2302`).
- `GET /api/history?since=24h` — historical readings since a Unix timestamp or relative value (`24h`, `30m`, `now-24h`).
- `GET /api/stream` — SSE stream of readings (`event: reading`).

SSE example:

```bash
curl -N http://localhost:8000/api/stream
```
