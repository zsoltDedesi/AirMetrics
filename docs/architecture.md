# Architecture

## System Overview

AirMetrics is a small hardware-aware monitoring stack.

```text
Raspberry Pi sensors -> Backend sampler services -> SQLite
                                  |
                                  +-> FastAPI REST endpoints
                                  +-> Server-Sent Events stream
                                                |
                                                v
                                      Vue dashboard
```

The backend is the system of record. It owns sensor reads, threshold filtering, buffering, SQLite persistence, retention cleanup, and health checks. The frontend displays live and historical sensor data.

## Main Components

### Frontend

Purpose:

- Render the local AirMetrics dashboard.
- Show latest DS18B20 and AM2302/DHT22 values.
- Display historical readings through a chart.
- Call backend health/history endpoints and subscribe to live readings.

Technology:

- Framework: Vue 3
- State management: Vue component state; Pinia is installed but not currently central to the visible dashboard flow.
- UI library: Naive UI
- Charting: Apache ECharts through `vue-echarts`
- Build tool: Vite
- API client: Axios

Important folders:

```text
Frontend/src/
├── api/
├── assets/
├── composables/
├── components/
├── styles/
├── utils/
└── views/
```

Responsibilities:

- Render user interface.
- Handle client-side interaction.
- Call backend APIs.
- Manage local UI state.
- Open and close the SSE connection.
- Display sensor values and history data.
- Keep reusable frontend runtime logic in composables and utilities.

Should avoid:

- Duplicating backend sampling or retention rules.
- Direct database access.
- Hardware assumptions inside UI components.
- Hidden side effects that survive component unmount.

### Backend

Purpose:

- Read local hardware sensors when the selected sensor mode enables them.
- Emit readings only when configured thresholds are exceeded.
- Persist readings to SQLite.
- Expose REST APIs and a Server-Sent Events stream.
- Report liveness and hardware-aware readiness.

Technology:

- Framework: FastAPI
- API style: JSON REST endpoints plus Server-Sent Events
- Authentication: none currently
- Background jobs: asyncio tasks for sampling, buffer flushing, and retention cleanup
- External integrations: Raspberry Pi 1-Wire sysfs and GPIO sensor libraries
- Sensor runtime modes: `hardware`, `degraded`, `mock`, and `disabled`

Important folders:

```text
Backend/app/
├── api/
├── sensors/
├── services/
├── utils/
├── db.py
├── main.py
└── stream.py
```

Responsibilities:

- Expose APIs under `/api`.
- Validate settings at startup.
- Coordinate sensor drivers and sampler services.
- Apply backend-side physical-range validation before readings are emitted.
- Apply AM2302-specific median confirmation filtering before threshold emission.
- Buffer emitted readings.
- Coordinate SQLite persistence.
- Publish live readings to SSE subscribers.
- Clean up tasks and hardware resources during shutdown.

Should avoid:

- UI-specific logic.
- Unstructured environment reads outside the settings layer.
- Hardware reads directly inside API handlers.
- Mixing new large workflows into route handlers when a service module would be clearer.

### Database

Database type:

- SQLite

Responsibilities:

- Store persisted sensor readings.
- Support history queries filtered by timestamp.
- Support retention cleanup.

Important entities:

| Entity | Purpose |
| --- | --- |
| `readings` | Stores emitted sensor readings with sensor name, temperature, optional humidity, and Unix timestamp. |

Schema change approach:

- No migration framework is currently present.
- Schema is created in `Backend/app/db.py` during database connection setup.
- Any schema change should be deliberate, documented, and tested against existing data before deployment to a Raspberry Pi.

### External Services

| Service or Boundary | Purpose | Risk or Constraint |
| --- | --- | --- |
| DS18B20 1-Wire sysfs | Temperature readings from `/sys/bus/w1/devices` | Requires Raspberry Pi 1-Wire setup and correct `DS18B20_DEVICE_ID`. |
| AM2302/DHT22 GPIO | Temperature and humidity readings | Requires GPIO access, device wiring, and Adafruit DHT/Blinka support. |
| GitHub Container Registry | Stores backend Docker image | Workflow requires package write permission and lowercase image name. |

## Data Flow

### Live Reading Flow

```text
1. Sensor driver reads physical sensor data.
2. Sampler validates the reading against sensor-specific physical limits.
3. Sampler creates a Reading model.
4. AM2302 readings pass through median confirmation filtering.
5. Sampler checks temperature and humidity thresholds.
6. Reading is appended to the in-memory buffer.
7. Reading is published to SseHub.
8. /api/stream sends the reading to subscribed frontend clients.
9. Frontend updates displayed sensor values.
```

### History Flow

```text
1. Sampler emits significant readings into the buffer.
2. Count-based or periodic flush writes the buffer to SQLite.
3. Frontend requests /api/history?since=<value>.
4. Backend parses the since value and queries SQLite.
5. Frontend renders returned readings in the chart component.
```

### Health Flow

```text
1. Client calls /api/health/live for process liveness.
2. Client calls /api/health/ready for database and sensor readiness.
3. Backend reports hardware-sensitive readiness flags.
```

## Architectural Boundaries

### UI Layer

Allowed:

- Display data.
- Trigger user actions.
- Handle client-side interaction.
- Show validation or error messages.
- Subscribe to the backend SSE stream.

Avoid:

- Complex domain decisions.
- Database logic.
- Hardcoded backend sampling behavior.

### API Layer

Allowed:

- Request and response handling.
- Basic input validation.
- Delegation to services, database access helpers, or app state.

Avoid:

- Hardware reads directly in route handlers.
- Large business workflows directly inside endpoints.
- Duplicated parsing or transformation logic across endpoints.

### Service Layer

Allowed:

- Sampling rules.
- Background task coordination.
- Health checks.
- Runtime configuration loading.

Avoid:

- UI formatting.
- Framework-specific request handling where possible.

### Data Access Layer

Allowed:

- SQLite connection setup.
- Persistence operations.
- Query-specific transformations into `Reading` models.

Avoid:

- UI-specific output formatting.
- Sensor hardware policy decisions.

## Architectural Rules

- Keep responsibilities separated by layer.
- Prefer explicit data flow over hidden coupling.
- Avoid circular dependencies.
- Keep domain rules close to backend domain or service modules.
- Keep reusable logic in services or utilities, not duplicated in endpoints or UI components.
- Prefer simple architecture until the project clearly needs more structure.
- Keep hardware-specific code isolated under `Backend/app/sensors/`.

## Known Constraints

| Constraint | Explanation | Impact |
| --- | --- | --- |
| Hardware-dependent backend validation | Full hardware validation still requires Raspberry Pi device paths and GPIO access. | Use `SENSOR_MODE=mock`, `degraded`, or `disabled` only when hardware-free startup is intended. |
| SQLite local storage | Data is stored in a local file under the configured `DB_PATH`. | Deployment is simple, but multi-instance scaling is not supported. |
| In-memory buffer | Recent readings are buffered before count-based or periodic flush. | Readings can be lost if the process exits before a flush. |
| No auth | API endpoints currently have no authentication. | Keep the service on a trusted network unless auth is added. |
| Permissive CORS | Backend currently allows all origins. | Restrict before exposing beyond local development/trusted network. |
| Backend-only CI image workflow | Current GitHub workflow publishes only the backend image. | Frontend deployment is not automated. |

## Open Architecture Questions

| Question | Context | Status |
| --- | --- | --- |
| Should frontend deployment be automated? | Current CI/CD only publishes backend image. | open |
| Should API authentication be added? | Current API is suitable only for trusted local networks. | open |
