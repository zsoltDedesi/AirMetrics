# Testing Strategy

## Purpose

This document describes how AirMetrics should be validated.

Use this file when adding features, fixing bugs, changing domain logic, modifying API behavior, or changing deployment behavior.

## Current State

The repository does not currently contain a dedicated automated test suite.

Validation is therefore split into:

- backend syntax checks,
- frontend build checks,
- endpoint smoke checks,
- manual browser checks,
- Raspberry Pi hardware validation.

## Test Types

### Unit Tests

Purpose:

- Validate isolated functions, services, and domain rules.

Use when:

- A function has important logic.
- A bug was caused by incorrect logic.
- A rule can be tested without hardware or external systems.

Good candidates:

- `parse_since`
- `Sampler._should_emit`
- `validate_sensor_data`
- SSE formatting helpers
- settings validation edge cases
- sensor-mode startup helpers with mocked drivers

### Integration Tests

Purpose:

- Validate interaction between components.

Use when:

- API endpoints interact with app state, services, or database.
- SQLite query or persistence behavior matters.
- Sensor boundaries can be simulated with test doubles.

Good candidates:

- `/api/history` with a temporary SQLite database.
- `/api/sensors/{sensor_name}/latest` with mocked sampler state.
- `/api/health/ready` with mocked DB and sensor drivers.

### End-to-End Tests

Purpose:

- Validate complete user flows.

Use when:

- The dashboard, backend API, and live updates must work together.
- Raspberry Pi hardware behavior needs release validation.

Good candidates:

- Dockerized backend on target hardware.
- Browser dashboard connected to live sensor stream.
- History chart after readings have been persisted.

## When to Add or Update Tests

Add or update tests when:

- Business or domain logic changes.
- API behavior changes.
- Data transformation changes.
- Database behavior changes.
- A bug is fixed.
- A regression risk exists.
- A new edge case is discovered.

Tests may be skipped only when:

- The change is documentation-only.
- The change is purely visual and no test framework exists for it.
- The project currently has no test setup for the affected layer.
- Hardware required for validation is unavailable.

If tests are skipped, mention why in the final summary.

## Validation Commands

Backend syntax check:

```bash
cd Backend
python -m compileall app
```

Backend local runtime check:

```bash
cd Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

This requires a valid `Backend/airmetrics.env` and expected hardware access.

Backend Docker runtime check on target hardware:

```bash
cd Backend
docker compose up --build -d
docker compose ps
```

Backend endpoint smoke checks:

```bash
curl http://localhost:8000/api/health/live
curl http://localhost:8000/api/health/ready
curl 'http://localhost:8000/api/history?since=24h'
curl -N http://localhost:8000/api/stream
```

Frontend install and build:

```bash
cd Frontend
npm install
npm run build
```

Frontend preview:

```bash
cd Frontend
npm run preview
```

No project-specific `pytest`, `npm run test`, lint, or format scripts are currently configured.

### Database

```bash
# No migration or seed commands are currently configured.
# Validate database behavior through backend startup and endpoint smoke checks.
```

### Docker

```bash
cd Backend
docker compose config
docker compose up -d --build
```

### Security and Audit

```bash
# Optional when tools are installed:
cd Frontend
npm audit

# Optional when pip-audit is installed:
cd Backend
pip-audit -r requirements.txt
```

## Manual Validation Checklist

Use this checklist when automated tests are not enough.

- [ ] Backend starts with valid `Backend/airmetrics.env`.
- [ ] `/api/health/live` returns a successful liveness response.
- [ ] `/api/health/ready` reflects DB and sensor readiness.
- [ ] `/api/history?since=24h` returns a valid JSON response.
- [ ] `/api/stream` stays open and emits readings or ping events.
- [ ] Dashboard renders without browser console errors.
- [ ] Health request reaches the backend.
- [ ] SSE stream updates DS18B20 and AM2302 values.
- [ ] History chart loads data for the configured interval.
- [ ] No server error appears in logs.
- [ ] Existing behavior was not accidentally removed.

## Bug Fix Validation

For bug fixes:

- [ ] Reproduce the original bug if possible.
- [ ] Confirm the bug no longer happens.
- [ ] Add a regression test if practical.
- [ ] Check nearby behavior that could be affected.
- [ ] Mention hardware validation limits if the bug depends on sensors.

## API Validation

For API changes:

- [ ] Request validation works.
- [ ] Success response is correct.
- [ ] Error response is correct.
- [ ] Status codes are appropriate.
- [ ] Existing endpoint paths remain compatible unless the task requires a change.
- [ ] API documentation is updated if applicable.

## Frontend Validation

For frontend changes:

- [ ] Component renders correctly.
- [ ] User interaction works.
- [ ] Error states are visible where relevant.
- [ ] SSE connections are closed on component unmount.
- [ ] Responsive layout is acceptable.
- [ ] No unnecessary state duplication was introduced.
- [ ] `npm run build` passes.

## Database Validation

For database changes:

- [ ] Existing SQLite data is considered.
- [ ] Schema initialization remains valid.
- [ ] Indexes support expected history queries.
- [ ] Retention behavior is not accidentally weakened.
- [ ] Rollback risk is understood.

## Hardware Validation Checklist

- [ ] 1-Wire is enabled on the Raspberry Pi.
- [ ] DS18B20 appears under `/sys/bus/w1/devices/28-*`.
- [ ] `SENSOR_MODE` is set intentionally for the validation target.
- [ ] `DS18B20_DEVICE_ID` matches the real device folder when `SENSOR_MODE=hardware`.
- [ ] AM2302/DHT22 is wired to the configured GPIO pin.
- [ ] Docker container has required GPIO devices mounted.
- [ ] `/var/lib/airmetrics` exists and is writable.
- [ ] `Backend/airmetrics.env` is mounted read-only into the container.
