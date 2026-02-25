# AirMetrics

AirMetrics is a small sensor + API stack for collecting and serving environmental readings (temperature/humidity) from a Raspberry Pi.

> Note: This is a sandbox / learning project created for experimentation. It is not a generic, production-ready template and it contains environment- and hardware-specific assumptions.

## Repository layout

- `Backend/` — FastAPI service: reads sensors, buffers readings, persists to SQLite, and exposes an HTTP API (plus SSE stream).
- `Frontend/` — Vue 3 + Vite frontend (currently scaffolded).

## Quickstart (Backend on Raspberry Pi via Docker)

### Host prerequisites

- Enable 1‑Wire and load `w1-gpio` and `w1-therm` (for DS18B20).
- Ensure `/var/lib/airmetrics` exists and is writable (DB is stored here).
- Ensure GPIO devices are available for AM2302: `/dev/gpiomem`, `/dev/gpiochip0` (and sometimes `/dev/mem` depending on backend probing).

### Configure env

Create `Backend/airmetrics.env` from the example:

```bash
cp Backend/airmetrics.env.example Backend/airmetrics.env
```

Set at least:

- `DB_PATH=/var/lib/airmetrics/airmetrics.db`
- `DS18B20_DEVICE_ID=28-...` (your 1‑Wire device folder name)

### Build and run

```bash
cd Backend
docker compose up --build -d
```

### Health checks

```bash
curl http://localhost:8000/api/health/live
curl http://localhost:8000/api/health/ready
```

## Development docs

- Backend: `Backend/README.md`
- Frontend: `Frontend/README.md`
