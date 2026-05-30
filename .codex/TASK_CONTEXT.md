# Task Context

## Purpose

This is a rolling memory file for AI coding agents.

Use it to preserve short-term project context between tasks without overloading `AGENTS.md`.

Keep this file concise. Remove outdated details when they no longer matter.

## Current State

- Backend is a FastAPI service for Raspberry Pi sensor collection.
- Backend reads DS18B20 and AM2302/DHT22 sensors, buffers significant readings, persists to SQLite, and exposes REST plus SSE APIs under `/api`.
- Frontend is a Vue 3 + Vite dashboard using Naive UI, Axios, Chart.js, and `vue-chart-3`.
- Backend Docker deployment targets Raspberry Pi ARM64 and publishes to GHCR through GitHub Actions.
- Automated test suite is not configured yet.
- API authentication is not implemented; current assumption is trusted local network usage.

## Recent Meaningful Changes

| Date | Change | Files / Area |
| --- | --- | --- |
| 2026-05-30 | Added standard agent documentation structure. | `AGENTS.md`, `docs/`, `.codex/` |
| 2026-05-30 | Added project-specific contract and operational docs. | `docs/API_CONTRACT.md`, `docs/DATABASE.md`, `docs/DEPLOYMENT.md`, `docs/DESIGN.md`, `docs/IMPLEMENTATION_PLAN.md` |
| 2026-05-30 | Corrected frontend API base example to include `/api`. | `Frontend/airmetrics.env.example` |
| 2026-05-30 | Refactored backend wiring/sampler/API formatting and frontend health/SSE/history logic. | `Backend/app/`, `Frontend/src/` |

## Validation Already Run

| Date | Command | Result |
| --- | --- | --- |
| 2026-05-30 | Documentation structure and placeholder search with `find`/`rg`. | passed |
| 2026-05-30 | Runtime tests | not run; documentation-focused changes and Raspberry Pi hardware unavailable |
| 2026-05-30 | `python3 -m compileall app` from `Backend/` | passed |
| 2026-05-30 | `npm run build` from `Frontend/` | passed |

## Known Issues

| Issue | Impact | Suggested Next Step |
| --- | --- | --- |
| No automated tests | Regression risk for backend and frontend changes. | Add targeted backend unit tests first. |
| Hardware-dependent backend startup | Local validation is limited away from Raspberry Pi. | Add mock sensor mode or test doubles. |
| API has no authentication | Unsafe for public exposure. | Keep on trusted network or add auth before exposure. |
| CORS is permissive | Broad browser access if network-exposed. | Restrict origins before production-style deployment. |
| `FLUSH_EVERY_READINGS` not implemented by flusher | Config suggests count-based flushing that does not currently happen. | Implement or remove/document the setting. |

## Current Assumptions

- Deployment target is a Raspberry Pi with Docker and sensor hardware attached.
- SQLite database is local to the host and mounted into the container.
- Frontend `VITE_API_BASE_BACKEND_URL` includes the `/api` prefix unless a proxy rewrites paths.
- All current backend routes are under `/api`.

## Next Recommended Steps

1. Add backend unit tests for `parse_since` and `Sampler._should_emit`.
2. Add sensor mock mode for hardware-free backend development.
3. Add AM2302 history visualization and configurable history range UI.
