# Technical Decisions

## Purpose

This document records important technical decisions and their reasoning.

Use it when a decision affects architecture, dependencies, persistence, API design, deployment, testing, or long-term maintainability.

Do not use it for every small implementation detail.

## Decision Template

```md
## YYYY-MM-DD - Decision title

Status: accepted / rejected / changed / superseded

Context:

Decision:

Reasoning:

Consequences:

Related files:
```

---

## 2026-05-29 - Use FastAPI for the backend

Status: accepted

Context:

AirMetrics needs a small HTTP API with async background work and a live stream endpoint.

Decision:

Use FastAPI as the backend application framework.

Reasoning:

FastAPI provides async request handling, lifespan hooks, typed endpoint code, and straightforward JSON APIs. It also supports returning Server-Sent Events through streaming responses.

Consequences:

Backend code should preserve async boundaries and keep startup/shutdown behavior in the FastAPI lifespan.

Related files:

- `Backend/app/main.py`
- `Backend/app/api/`

---

## 2026-05-29 - Use SQLite for local persistence

Status: accepted

Context:

The project runs on a Raspberry Pi and needs simple local storage for sensor history.

Decision:

Use SQLite as the persisted readings database.

Reasoning:

SQLite avoids a separate database service, keeps deployment simple, and is sufficient for local sensor history. WAL mode and indexes improve normal query/write behavior for this small workload.

Consequences:

Multi-instance backend scaling is not supported. Schema changes require care because no migration framework is currently configured.

Related files:

- `Backend/app/db.py`
- `Backend/docker-compose.yml`
- `docs/development.md`

---

## 2026-05-29 - Buffer readings before database writes

Status: accepted

Context:

Sensor readings may arrive frequently, but writing every emitted reading immediately would couple sampling to SQLite write latency.

Decision:

Store emitted readings in an in-memory buffer and flush them periodically to SQLite.

Reasoning:

This keeps sensor sampling and live streaming responsive while reducing database write frequency.

Consequences:

Recent readings can be lost if the process terminates before the next flush. Shutdown should flush the remaining buffer where possible.

Related files:

- `Backend/app/main.py`
- `Backend/app/services/tasks.py`

---

## 2026-05-29 - Emit only significant sensor changes

Status: accepted

Context:

The project should avoid noisy storage and dashboard updates when sensor values are nearly unchanged.

Decision:

Emit the first valid reading and later emit readings only when configured temperature or humidity deltas are reached.

Reasoning:

Threshold-based emission reduces storage volume and live stream noise.

Consequences:

History behaves like a change log rather than a fixed-interval time series.

Related files:

- `Backend/app/services/sampler.py`
- `Backend/airmetrics.env.example`
- `docs/domain.md`

---

## 2026-05-29 - Use Server-Sent Events for live data

Status: accepted

Context:

The frontend needs live backend-to-browser updates, but it does not need bidirectional communication.

Decision:

Use Server-Sent Events for live readings.

Reasoning:

SSE is simple, browser-native through `EventSource`, and sufficient for one-way sensor updates.

Consequences:

The backend maintains subscriber queues and sends periodic ping events. If bidirectional control is needed later, WebSockets may need to be evaluated.

Related files:

- `Backend/app/stream.py`
- `Backend/app/api/stream.py`
- `Frontend/src/views/HomeView.vue`

---

## 2026-05-29 - Keep hardware drivers in the backend

Status: accepted

Context:

Sensor access is Raspberry Pi and OS dependent.

Decision:

Keep sensor drivers under `Backend/app/sensors/` and expose sensor state through backend APIs rather than frontend logic.

Reasoning:

This isolates hardware dependencies and prevents API handlers or UI components from directly owning sensor reads.

Consequences:

Local backend development without hardware requires mocks, targeted tests, or isolated module validation.

Related files:

- `Backend/app/sensors/`
- `Backend/app/services/sampler.py`

---

## 2026-05-29 - Build backend image for ARM64

Status: accepted

Context:

The backend is intended to run on Raspberry Pi hardware.

Decision:

Build and publish the backend Docker image for `linux/arm64`.

Reasoning:

ARM64 matches the target deployment environment.

Consequences:

The current GitHub Actions workflow publishes only the backend image. Frontend deployment is not automated.

Related files:

- `.github/workflows/backend-image.yml`
- `Backend/Dockerfile`

---

## 2026-05-30 - Use Apache ECharts for frontend history charts

Status: accepted

Context:

The dashboard history charts need to render dense temperature and humidity time series inside constrained dashboard cards without overflowing into adjacent UI. The previous Chart.js implementation showed layout overflow with current production-like data.

Decision:

Use Apache ECharts through the `vue-echarts` wrapper for frontend history charts.

Reasoning:

ECharts provides robust time-series rendering, built-in clipping, contained grid labels, confined tooltips, and good resize behavior through the Vue wrapper. This keeps the chart implementation inside the frontend component layer without changing backend API contracts.

Consequences:

The frontend depends on `echarts` and `vue-echarts` instead of `chart.js` and `vue-chart-3`. The production bundle is larger, so future frontend performance work may split chart code into a separate chunk if needed.

Related files:

- `Frontend/src/components/LineChartWrapper.vue`
- `Frontend/package.json`
- `docs/DESIGN.md`

---

## Known Gaps

- No automated backend or frontend test suite is currently present.
- No dedicated frontend CI workflow is present.
- Backend startup is tightly coupled to sensor availability.
- `FLUSH_EVERY_READINGS` exists in settings but is not currently used by the flusher.
- CORS is permissive and should be restricted before exposing the service outside a trusted network.
