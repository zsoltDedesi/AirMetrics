# Context Map for Agents

## Purpose

This file helps AI coding agents quickly find the right AirMetrics project context.

Use this as a navigation map before starting a task.

## Where to Look First

| Task Type | Start Here |
| --- | --- |
| Architecture change | `docs/architecture.md` |
| New feature | `docs/domain.md`, then relevant source files |
| Bug fix | failing behavior, logs, related module |
| Test update | `docs/testing.md` |
| Setup issue | `docs/development.md` |
| Workflow or release issue | `docs/workflows.md` |
| API contract change | `docs/API_CONTRACT.md` |
| Database change | `docs/DATABASE.md` |
| Deployment change | `docs/DEPLOYMENT.md` |
| Design/UI change | `docs/DESIGN.md` |
| Implementation planning | `docs/IMPLEMENTATION_PLAN.md` |
| Rolling task state | `.codex/TASK_CONTEXT.md` |
| Refactor | `docs/architecture.md`, existing code patterns |
| Major technical decision | `docs/decisions.md` |
| Unknown project context | `AGENTS.md`, then this file |

## Important Source Areas

| Area | Path | Purpose |
| --- | --- | --- |
| Backend app | `Backend/app/` | FastAPI app, sensor services, SSE, database access. |
| Backend API | `Backend/app/api/` | HTTP and SSE endpoint routers. |
| Backend services | `Backend/app/services/` | Settings, sampler, background tasks, health checks. |
| Sensor drivers | `Backend/app/sensors/` | DS18B20 and AM2302 hardware drivers. |
| Frontend | `Frontend/src/` | Vue dashboard, API clients, components, styles. |
| Frontend API clients | `Frontend/src/api/` | Axios client and backend endpoint helpers. |
| Deployment | `Backend/Dockerfile`, `Backend/docker-compose.yml` | Backend image and Raspberry Pi runtime. |
| CI/CD | `.github/workflows/` | GitHub Actions workflows. |
| Documentation | `docs/` | Project knowledge. |
| Agent support | `.codex/` | Agent-specific guidance. |

## Files to Read by Task

### New Feature

Read:

1. `AGENTS.md`
2. `.codex/context-map.md`
3. `docs/domain.md`
4. `docs/architecture.md`
5. Relevant project-specific docs
6. Relevant source files
7. `docs/testing.md`

### Bug Fix

Read:

1. `AGENTS.md`
2. Error message, logs, or failing behavior
3. Related source files
4. Related tests if present
5. `docs/testing.md`
6. `.codex/TASK_CONTEXT.md`

### Refactor

Read:

1. `AGENTS.md`
2. `docs/architecture.md`
3. Existing implementation patterns
4. Related tests if present
5. Relevant project-specific docs if contracts may be affected

### Setup or Tooling Change

Read:

1. `AGENTS.md`
2. `docs/development.md`
3. Config files
4. `docs/workflows.md` if CI or release is affected
5. `docs/DEPLOYMENT.md` if runtime behavior is affected

### API Change

Read:

1. `AGENTS.md`
2. `docs/API_CONTRACT.md`
3. `docs/architecture.md`
4. `docs/domain.md`
5. `Backend/app/api/`
6. `Backend/app/db.py`
7. `docs/testing.md`

### Database Change

Read:

1. `AGENTS.md`
2. `docs/DATABASE.md`
3. `docs/architecture.md`
4. `Backend/app/db.py`
5. `docs/development.md`
6. `docs/testing.md`

### Deployment Change

Read:

1. `AGENTS.md`
2. `docs/DEPLOYMENT.md`
3. `docs/workflows.md`
4. `Backend/Dockerfile`
5. `Backend/docker-compose.yml`
6. `.github/workflows/`

### Sensor or Hardware Change

Read:

1. `AGENTS.md`
2. `docs/domain.md`
3. `Backend/app/sensors/`
4. `Backend/app/services/sampler.py`
5. `Backend/docker-compose.yml`
6. `docs/testing.md`

### Frontend Change

Read:

1. `AGENTS.md`
2. `docs/DESIGN.md`
3. `docs/architecture.md`
4. `Frontend/src/views/HomeView.vue`
5. `Frontend/src/components/`
6. `Frontend/src/api/`
7. `docs/testing.md`

## Do Not Touch Without Explicit Request

- Production or deployment configuration.
- Secrets or credentials.
- Real `airmetrics.env` files.
- Database schema behavior.
- Generated build output.
- Lockfiles, unless dependency changes require it.
- Public API contracts, unless the task requires it.
- Raspberry Pi device mounts, unless deployment behavior is part of the task.

## Final Response Requirements

At the end of the task, summarize:

- Changed files
- What changed
- Validation performed
- Known risks or assumptions
