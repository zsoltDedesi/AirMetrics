# Deployment Documentation

## Purpose

This document describes how AirMetrics is deployed and what operational assumptions must be preserved.

## Deployment Topology

Current backend deployment target:

```text
Raspberry Pi hardware sensors
  -> Docker backend container
  -> local SQLite file under /var/lib/airmetrics
  -> HTTP API on port 8000
```

The frontend is a separate Vue/Vite app. No frontend deployment workflow is currently configured.

## Containers

| Container | Purpose | Exposed Port | Internal Port |
| --- | --- | ---: | ---: |
| `airmetrics-backend` | Serves FastAPI API, samplers, SSE, SQLite persistence. | 8000 | 8000 |

## Image

Backend image:

```text
ghcr.io/zsoltdedesi/airmetrics-backend:latest
```

GitHub Actions builds and pushes:

- `latest`
- `backend-v*.*.*` tag name on tag push
- `manual-<short-sha>` on manual workflow dispatch

Target platform:

```text
linux/arm64
```

## Runtime Mounts and Devices

Volumes:

| Host Path | Container Path | Purpose |
| --- | --- | --- |
| `./airmetrics.env` | `/app/airmetrics.env` | Backend runtime configuration. |
| `/var/lib/airmetrics` | `/var/lib/airmetrics` | Persistent SQLite data. |
| `/sys/bus/w1/devices` | `/sys/bus/w1/devices` | DS18B20 1-Wire access. |
| `/proc/device-tree` | `/proc/device-tree` | Raspberry Pi hardware detection support. |
| `/sys/firmware/devicetree/base` | `/sys/firmware/devicetree/base` | Raspberry Pi hardware detection support. |

Devices:

| Device | Purpose |
| --- | --- |
| `/dev/gpiomem` | GPIO access. |
| `/dev/gpiochip0` | GPIO access. |
| `/dev/mem` | Fallback hardware probing used by some GPIO stacks. |

## Reverse Proxy Assumptions

- No reverse proxy is currently documented in the repository.
- If a proxy is added, preserve SSE behavior for `/api/stream`.
- Disable proxy buffering for SSE. The backend already sends `X-Accel-Buffering: no`.
- Document public domain, TLS termination, and path routing here if added.

## Environment Variables

Backend variables are loaded from `/app/airmetrics.env` inside the container.

| Name | Required | Runtime | Description |
| --- | ---: | --- | --- |
| `SENSOR_MODE` | no | backend | Sensor runtime mode: `hardware`, `degraded`, `mock`, or `disabled`; defaults to `hardware`. |
| `DS18B20_DEVICE_ID` | yes in `hardware` mode | backend | Linux 1-Wire sensor folder. |
| `DB_PATH` | yes | backend | Absolute SQLite file path. |
| `DS18B20_SAMPLING_INTERVAL_SECONDS` | no | backend | DS18B20 polling interval. |
| `AM2302_CALIBRATION_OFFSET` | no | backend | AM2302 temperature calibration offset. |
| `AM2302_HUMIDITY_CALIBRATION_OFFSET` | no | backend | AM2302 relative humidity calibration offset. |
| `AM2302_SAMPLING_INTERVAL_SECONDS` | no | backend | AM2302 polling interval. |
| `THRESHOLD_DELTA_T_HIGH` | no | backend | DS18B20 significant-change threshold. |
| `THRESHOLD_DELTA_T_LOW` | no | backend | AM2302 temperature threshold. |
| `THRESHOLD_DELTA_RH` | no | backend | AM2302 humidity threshold. |
| `BUFFER_MAX_READINGS` | no | backend | In-memory buffer length. |
| `FLUSH_EVERY_SECONDS` | no | backend | Periodic database flush interval. |
| `FLUSH_EVERY_READINGS` | no | backend | Count threshold that triggers an immediate database flush. |
| `RETENTION_INTERVAL_SECONDS` | no | backend | Retention task interval. |
| `RETENTION_HOURS` | no | backend | Data retention window. |

## Deployment Steps

Prepare host:

```bash
sudo mkdir -p /var/lib/airmetrics
sudo chown "$USER":"$USER" /var/lib/airmetrics
```

Configure backend:

```bash
cd Backend
cp airmetrics.env.example airmetrics.env
# edit SENSOR_MODE, DS18B20_DEVICE_ID, and DB_PATH as needed
```

Start or update container:

```bash
cd Backend
docker compose pull
docker compose up -d
```

Build locally instead of pulling:

```bash
cd Backend
docker compose up -d --build
```

## Migrations and Seeds

Migrations:

```bash
# No migration command is currently configured.
```

Seeds:

```bash
# No seed command is currently configured.
```

Schema is created during backend startup.

## Smoke Checks

After deployment, check:

- [ ] Container starts successfully.
- [ ] `docker compose ps` shows healthy or running backend.
- [ ] `curl http://localhost:8000/api/health/live` succeeds.
- [ ] `curl http://localhost:8000/api/health/ready` reports expected DB and sensor state.
- [ ] `curl -N http://localhost:8000/api/stream` stays open and sends events.
- [ ] `/var/lib/airmetrics/airmetrics.db` exists after readings flush.
- [ ] Logs do not show startup configuration errors.

## Background Jobs and Schedulers

The backend starts these background tasks in the FastAPI lifespan:

- Sensor samplers for sensors enabled by `SENSOR_MODE`.
- Buffer flusher.
- Retention cleanup.

Constraints:

- The backend is intended as a single running replica.
- Running multiple replicas against the same local hardware and SQLite file is not supported.
- If a task fails internally, current behavior is to print errors and continue where implemented.
- `SENSOR_MODE=hardware` keeps production-style fail-fast startup when required hardware is unavailable.
- `SENSOR_MODE=disabled` starts without sensor drivers or sampler tasks, but still requires a valid `DB_PATH`.
