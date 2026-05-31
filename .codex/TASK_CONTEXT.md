# Task Context

## Purpose

This is a rolling memory file for AI coding agents.

Use it to preserve short-term project context between tasks without overloading `AGENTS.md`.

Keep this file concise. Remove outdated details when they no longer matter.

## Current State

- Backend is a FastAPI service for Raspberry Pi sensor collection.
- Backend reads DS18B20 and AM2302/DHT22 sensors when `SENSOR_MODE` enables them, filters AM2302 noise, buffers significant validated readings, persists to SQLite, and exposes REST plus SSE APIs under `/api`.
- Backend sensor modes are `hardware`, `degraded`, `mock`, and `disabled`; `hardware` remains the default fail-fast mode.
- Frontend is a Vue 3 + Vite dashboard using Naive UI, Axios, Apache ECharts, and `vue-echarts`.
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
| 2026-05-30 | Rebuilt frontend dashboard from Figma Make concept with metric cards, status strip, range controls, CSV export, and temperature/humidity charts. | `Frontend/src/`, `docs/DESIGN.md`, `docs/IMPLEMENTATION_PLAN.md` |
| 2026-05-30 | Added Material-style frontend design tokens and rewired dashboard CSS/chart colors to use tokenized colors, typography, and shapes where practical. | `Frontend/src/styles/`, `Frontend/src/components/LineChartWrapper.vue`, `docs/DESIGN.md` |
| 2026-05-30 | Replaced Chart.js history charts with Apache ECharts via `vue-echarts` and constrained chart rendering inside dashboard cards. | `Frontend/src/components/LineChartWrapper.vue`, `Frontend/package.json`, `docs/` |
| 2026-05-30 | Added frontend-only temperature chart outlier hiding for values outside `-40°C` to `85°C`, with a visible hidden-count badge. | `Frontend/src/components/LineChartWrapper.vue`, `docs/DESIGN.md` |
| 2026-05-30 | Opted backend image GitHub Actions workflow into Node.js 24 JavaScript action runtime. | `.github/workflows/backend-image.yml`, `docs/workflows.md` |
| 2026-05-31 | Added backend sensor runtime modes, mock sensors, physical-range reading validation, AM2302 failure tracking, and count-based buffer flushing. | `Backend/app/`, `Backend/airmetrics.env.example`, `docs/` |
| 2026-05-31 | Added AM2302-only 5-sample median filtering with 2-reading confirmation before threshold emission. | `Backend/app/services/reading_filter.py`, `Backend/app/services/sampler.py`, `Backend/app/main.py`, `docs/` |

## Validation Already Run

| Date | Command | Result |
| --- | --- | --- |
| 2026-05-30 | Documentation structure and placeholder search with `find`/`rg`. | passed |
| 2026-05-30 | Runtime tests | not run; documentation-focused changes and Raspberry Pi hardware unavailable |
| 2026-05-30 | `python3 -m compileall app` from `Backend/` | passed |
| 2026-05-30 | `npm run build` from `Frontend/` | passed |
| 2026-05-30 | Headless Chrome screenshots of Vite dashboard at 1280x900 and 390x1100. | passed; layout rendered without visible overlap |
| 2026-05-30 | `npm run build` after ECharts migration and headless Chrome dashboard screenshot at 1240x1050. | passed; Vite reported a large chunk warning from chart dependencies |
| 2026-05-30 | `npm run build` after chart outlier hiding and headless Chrome dashboard screenshot at 1240x1050. | passed; normal temperature range rendered without the `430°C` spike compressing the chart |
| 2026-05-31 | `python3 -m compileall app` from `Backend/` after backend sensor-mode changes. | passed |
| 2026-05-31 | Direct `validate_sensor_data` check for valid DS18B20/AM2302 values and invalid spike/humidity values. | passed |
| 2026-05-31 | `python3 -m compileall app` from `Backend/` after AM2302 filter changes. | passed |
| 2026-05-31 | Direct `MedianConfirmationFilter` check for first reading, single-spike suppression, and sustained-change emission. | passed |

## Known Issues

| Issue | Impact | Suggested Next Step |
| --- | --- | --- |
| No automated tests | Regression risk for backend and frontend changes. | Add targeted backend unit tests first. |
| API has no authentication | Unsafe for public exposure. | Keep on trusted network or add auth before exposure. |
| CORS is permissive | Broad browser access if network-exposed. | Restrict origins before production-style deployment. |
| AM2302 filter constants are not field-tuned | Default 5-sample median and 2-reading confirmation may need adjustment after real sensor observation. | Validate against Raspberry Pi hardware data. |
| Last cleanup time is not exposed by API | Frontend cannot display a real cleanup timestamp. | Add a backend status/config endpoint if this metric is needed. |
| ECharts increases frontend bundle size | Vite warns that the main production chunk exceeds 500 kB. | Consider route/component-level dynamic import or Rollup manual chunks if bundle size matters. |

## Current Assumptions

- Deployment target is a Raspberry Pi with Docker; sensor hardware is expected in `hardware` mode and optional by mode otherwise.
- SQLite database is local to the host and mounted into the container.
- Frontend `VITE_API_BASE_BACKEND_URL` includes the `/api` prefix unless a proxy rewrites paths.
- All current backend routes are under `/api`.

## Next Recommended Steps

1. Add backend unit tests for `parse_since`, `Sampler._should_emit`, reading validation, median filtering, and sensor-mode startup helpers.
2. Tune AM2302 filter constants after Raspberry Pi hardware observation.
3. Add backend-exposed operational status for cleanup timing and threshold values if the dashboard should show those as live metrics.
