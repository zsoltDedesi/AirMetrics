# Development Guide

## Requirements

- Runtime:
  - Backend: Python 3.11 compatible environment.
  - Frontend: Node.js compatible with the Vite version in `Frontend/package.json`.
  - Full backend runtime validation requires Raspberry Pi hardware.
- Package manager:
  - Backend: `pip`.
  - Frontend: `npm`.
- Database:
  - SQLite database file configured with `DB_PATH`.
- Docker:
  - Docker and Docker Compose for backend container deployment.
- Node.js:
  - Required for the Vue/Vite frontend.
- Python:
  - Required for the FastAPI backend.
- Other services:
  - DS18B20 sensor exposed through Linux 1-Wire sysfs at `/sys/bus/w1/devices`.
  - AM2302/DHT22 sensor available through GPIO and Adafruit DHT/Blinka dependencies.
  - Raspberry Pi device mounts for Dockerized 1-Wire and GPIO access.

## Local Setup

If you are outside the repository, enter the repository root:

```bash
cd AirMetrics
```

Install backend dependencies:

```bash
cd Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd Frontend
npm install
```

## Environment Variables

Create backend environment configuration:

```bash
cd Backend
cp airmetrics.env.example airmetrics.env
```

Backend variables:

| Name | Required | Example | Description |
| --- | ---: | --- | --- |
| `SENSOR_MODE` | no | `hardware` | Sensor runtime mode: `hardware`, `degraded`, `mock`, or `disabled`. |
| `DS18B20_DEVICE_ID` | yes in `hardware` mode | `28-000000000000` | Linux 1-Wire device folder under `/sys/bus/w1/devices`. |
| `DB_PATH` | yes | `/var/lib/airmetrics/airmetrics.db` | Absolute SQLite database file path. |
| `DS18B20_SAMPLING_INTERVAL_SECONDS` | no | `2.0` | Polling interval for DS18B20. |
| `AM2302_CALIBRATION_OFFSET` | no | `1.0` | Temperature calibration offset for AM2302. |
| `AM2302_SAMPLING_INTERVAL_SECONDS` | no | `2.0` | Polling interval for AM2302. |
| `THRESHOLD_DELTA_T_HIGH` | no | `0.125` | Temperature delta threshold for high-precision sensor readings. |
| `THRESHOLD_DELTA_T_LOW` | no | `0.3` | Temperature delta threshold for lower-precision sensor readings. |
| `THRESHOLD_DELTA_RH` | no | `1.0` | Relative humidity delta threshold. |
| `BUFFER_MAX_READINGS` | no | `10000` | Maximum in-memory buffer length. |
| `FLUSH_EVERY_SECONDS` | no | `300.0` | Periodic database flush interval. |
| `FLUSH_EVERY_READINGS` | no | `1000` | Count threshold that triggers an immediate database flush. |
| `RETENTION_INTERVAL_SECONDS` | no | `3600.0` | Retention task interval. |
| `RETENTION_HOURS` | no | `24` | Number of hours to retain readings. |

Optional backend values can stay empty in `airmetrics.env`; the settings loader ignores empty values and applies defaults.

Sensor modes:

| Mode | Behavior |
| --- | --- |
| `hardware` | Production-style mode. Required hardware must initialize successfully or startup fails. |
| `degraded` | Backend starts when one or both sensors are unavailable; only available sensors get samplers. |
| `mock` | Backend uses generated sensor readings for hardware-free development or demo. |
| `disabled` | Backend starts without sensor drivers or sampler tasks. |

Frontend environment:

| Name | Required | Example | Description |
| --- | ---: | --- | --- |
| `VITE_API_BASE_BACKEND_URL` | yes for frontend API calls | `http://localhost:8000/api` | Backend API base URL. Include `/api` when no Vite proxy is used. |

The SSE connection in `HomeView.vue` appends `/stream` to `VITE_API_BASE_BACKEND_URL`.

## Secret-Handling Rules

- Do not commit secrets.
- Keep real secrets in local env files or secret managers.
- Keep `airmetrics.env.example` files safe and non-sensitive.
- Document required variables without exposing real credentials.
- `Backend/airmetrics.env` and `Frontend/.env` are local runtime files and should not be committed.

## Run Locally

Backend local run:

```bash
cd Backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

This requires `Backend/airmetrics.env` and the expected hardware/device paths when `SENSOR_MODE=hardware`. Use `SENSOR_MODE=mock`, `degraded`, or `disabled` for hardware-free startup.

Frontend local run:

```bash
cd Frontend
npm run dev
```

Docker backend run on Raspberry Pi target:

```bash
cd Backend
docker compose up --build -d
```

Useful backend checks:

```bash
curl http://localhost:8000/api/health/live
curl http://localhost:8000/api/health/ready
curl -N http://localhost:8000/api/stream
```

## Build

Frontend build:

```bash
cd Frontend
npm run build
```

Backend container build and run:

```bash
cd Backend
docker compose up --build -d
```

The GitHub Actions workflow builds and publishes the backend Docker image for `linux/arm64`.

## Useful Commands

Backend syntax check:

```bash
cd Backend
python -m compileall app
```

Frontend preview:

```bash
cd Frontend
npm run preview
```

Stop backend Docker service:

```bash
cd Backend
docker compose down
```

View backend Docker logs:

```bash
cd Backend
docker compose logs -f backend
```

## Database

Database type:

- SQLite

Local connection:

```text
path: value of DB_PATH
default Docker host path: /var/lib/airmetrics/airmetrics.db
container path: /var/lib/airmetrics/airmetrics.db
```

Migration command:

```bash
# No migration framework is currently configured.
```

Seed command:

```bash
# No seed command is currently configured.
```

## Repository Layout

```text
Backend/
  app/
    api/          FastAPI routers
    sensors/      hardware drivers
    services/     settings, sampler, background jobs, health checks
    utils/        shared helpers
    db.py         Reading model and SQLite access
    main.py       app assembly and lifespan
    stream.py     SSE hub and formatting
  Dockerfile
  docker-compose.yml
  requirements.txt
  airmetrics.env.example

Frontend/
  src/
    api/          axios API clients
    components/   chart wrapper and UI components
    styles/       CSS
    views/        dashboard views
  package.json
  vite.config.js
  airmetrics.env.example
```

## Common Development Problems

### Dependency installation fails

Symptom:

- Backend or frontend dependency installation fails.

Possible solution:

- Check the Python or Node.js runtime version.
- Recreate the Python virtual environment if it is corrupted.
- Run `npm install` from `Frontend/`, not the repository root.

### Backend cannot start

Symptom:

- FastAPI startup exits with configuration or sensor errors.

Possible solution:

- Check `Backend/airmetrics.env`.
- Confirm `DB_PATH` is absolute and its parent directory exists and is writable.
- If `SENSOR_MODE=hardware`, confirm `DS18B20_DEVICE_ID` matches a real `/sys/bus/w1/devices/28-*` folder.
- If `SENSOR_MODE=hardware`, confirm Raspberry Pi sensor device paths are available.
- Use `SENSOR_MODE=mock`, `degraded`, or `disabled` when starting without the sensor extension board.

### Frontend cannot reach backend

Symptom:

- API calls fail from browser.

Possible solution:

- Check backend is running.
- Check `VITE_API_BASE_BACKEND_URL`.
- Include `/api` in the base URL when there is no proxy.
- Check CORS settings if using a different origin.

### SSE stream does not update

Symptom:

- Dashboard renders but live values remain empty.

Possible solution:

- Check `/api/stream` with `curl -N`.
- Check backend sampler logs.
- Confirm sensors are producing readings that exceed configured thresholds.

## Development Notes

- Keep local-only settings out of committed files.
- Do not commit secrets.
- Prefer `airmetrics.env.example` files for documenting required configuration.
- Document new setup steps in this file.
- Keep sensor I/O out of route handlers.
- Keep frontend API helpers under `Frontend/src/api/`.
