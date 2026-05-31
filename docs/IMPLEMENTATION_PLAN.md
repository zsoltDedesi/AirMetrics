# Implementation Plan

## Purpose

This document tracks implementation phases, MVP scope, completed milestones, and current follow-ups.

Use this file to help agents understand what is already done and what should come next.

## MVP Scope

In scope:

- Raspberry Pi backend runtime.
- DS18B20 temperature sampling.
- AM2302/DHT22 temperature and humidity sampling.
- Threshold-based emitted readings.
- SQLite persistence and retention.
- REST API for health, latest values, and history.
- SSE live reading stream.
- Basic Vue dashboard with latest values and history chart.
- Backend Docker image and Raspberry Pi compose deployment.

Out of scope for current MVP:

- Public internet exposure.
- Authentication and authorization.
- Multi-replica backend deployment.
- Remote database service.
- Automated frontend deployment.
- Full automated test suite.

## Phases

### Phase 1 - Backend Foundation

Goal:

- Establish FastAPI backend, settings, sensor drivers, database, and background tasks.

Status: done

Tasks:

- [x] FastAPI app and router prefix.
- [x] Settings loader with required env validation.
- [x] DS18B20 driver.
- [x] AM2302 driver.
- [x] Sampler service.
- [x] SQLite persistence.
- [x] Flusher and retention tasks.
- [x] Health, latest, history, and stream endpoints.

### Phase 2 - Frontend Dashboard

Goal:

- Display live and historical sensor data.

Status: in progress

Tasks:

- [x] Vue/Vite app.
- [x] API client helpers.
- [x] Health call.
- [x] SSE subscription.
- [x] Basic sensor value cards.
- [x] Basic history chart.
- [x] Basic health, stream, and history error states.
- [x] History loading state.
- [x] AM2302 history visualization.
- [x] Configurable history range UI.

### Phase 3 - Deployment

Goal:

- Run backend reliably on Raspberry Pi through Docker.

Status: in progress

Tasks:

- [x] Backend Dockerfile.
- [x] Raspberry Pi compose file.
- [x] GHCR image workflow.
- [x] ARM64 build target.
- [ ] Document reverse proxy setup if one is added.
- [ ] Add frontend deployment workflow if needed.

### Phase 4 - Hardening

Goal:

- Improve validation, failure handling, and maintainability.

Status: planned

Tasks:

- [ ] Add backend unit tests for `parse_since` and sampler thresholds.
- [ ] Add database tests with temporary SQLite file.
- [ ] Add API tests with mocked app state.
- [ ] Add frontend build/test workflow.
- [x] Add sensor mock mode for local development.
- [x] Add explicit sensor runtime modes for hardware, degraded, mock, and disabled startup.
- [x] Add backend-side physical-range validation for emitted readings.
- [x] Add AM2302 median confirmation noise filtering.
- [x] Use `FLUSH_EVERY_READINGS` for count-based database flushing.
- [ ] Restrict CORS before non-local exposure.
- [ ] Decide whether authentication is required.

## Completed Milestones

| Date | Milestone | Notes |
| --- | --- | --- |
| 2026-05-30 | Agent documentation structure added | Standard and project-specific docs created for future agent tasks. |
| 2026-05-30 | Backend image workflow documented | GHCR ARM64 backend image workflow described in docs. |
| 2026-05-30 | Figma-derived frontend dashboard added | Dashboard now has metric cards, status strip, range controls, temperature and humidity history charts. |
| 2026-05-30 | Material-style frontend token layer added | Colors, typography, shapes, dashboard CSS, and chart colors now use Material-style tokens where practical. |
| 2026-05-30 | History charts migrated to Apache ECharts | `vue-echarts` now renders temperature and humidity history within fixed chart surfaces. |
| 2026-05-31 | Sensor runtime modes and backend reading validation added | Backend can run in `hardware`, `degraded`, `mock`, or `disabled` mode; impossible readings are rejected before buffering. |
| 2026-05-31 | AM2302 noise filtering added | AM2302 emissions use 5-sample median smoothing plus 2-reading confirmation. |
| 2026-05-31 | Cleanup status exposed to dashboard | `/api/system/status` reports retention metadata and the frontend Last cleanup tile uses it. |

## Current Follow-Ups

| Item | Reason | Priority |
| --- | --- | --- |
| Add automated backend tests | Core parsing and sampler logic can be tested without hardware. | high |
| Tune AM2302 filter on Raspberry Pi hardware | Median confirmation constants may need field adjustment after real sensor observation. | medium |
| Decide auth/network exposure policy | API currently has no authentication and permissive CORS. | medium |

## Known Gaps

| Gap | Impact | Suggested Next Step |
| --- | --- | --- |
| No automated test suite | Regression risk grows with changes. | Start with backend unit tests for pure logic. |
| No migration tooling | Schema changes are risky after deployment. | Add migration strategy before incompatible DB changes. |
| AM2302 filter not field-tuned | Default 5-sample median and 2-reading confirmation may be too slow or too permissive in the final hardware setup. | Observe live data and tune if needed. |
| Frontend deployment not automated | Dashboard release process is manual or undefined. | Define desired frontend hosting/deployment model. |
