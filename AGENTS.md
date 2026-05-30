# Agent Instructions

## Project Goal

AirMetrics is a Raspberry Pi based environmental monitoring project for collecting, storing, and displaying temperature and humidity readings. It is for a local hardware setup where a FastAPI backend reads DS18B20 and AM2302/DHT22 sensors, persists readings to SQLite, and a Vue dashboard shows live and historical data.

The main technical goal is to keep sensor collection reliable on Raspberry Pi hardware while keeping the backend, frontend, deployment, and documentation simple enough for a small project.

## How to Work in This Repository

- Read this file before making changes.
- Inspect the relevant files before editing.
- Prefer small, focused changes.
- Do not rewrite unrelated code.
- Follow the existing naming, structure, and style.
- Avoid introducing new dependencies unless clearly justified.
- Do not change public APIs, database schemas, or deployment configuration unless the task explicitly requires it.
- Do not commit real `airmetrics.env` files. Use `airmetrics.env.example` as the documented contract.
- Treat `/var/lib/airmetrics` and Raspberry Pi device paths as runtime/deployment concerns, not repo-managed files.
- If a change affects architecture, update `docs/architecture.md`.
- If a change affects local setup, commands, or tooling, update `docs/development.md`.
- If a change affects domain rules or terminology, update `docs/domain.md`.
- If a change affects testing strategy or test commands, update `docs/testing.md`.
- If a significant technical decision is made, append it to `docs/decisions.md`.
- If a change affects API contracts, update `docs/API_CONTRACT.md`.
- If a change affects database behavior, update `docs/DATABASE.md`.
- If a change affects deployment, update `docs/DEPLOYMENT.md`.
- If a change affects the visual system, update `docs/DESIGN.md`.
- If implementation status changes meaningfully, update `docs/IMPLEMENTATION_PLAN.md`.
- After meaningful changes, update `.codex/TASK_CONTEXT.md`.

## Agent Workflow for Non-Trivial Changes

Before making non-trivial changes:

1. Read `AGENTS.md`.
2. Read `.codex/context-map.md`.
3. Select only the relevant docs for the task.
4. Inspect existing source files before editing.
5. Keep the change small and consistent with existing patterns.
6. Run validation from `docs/testing.md`.
7. Update project-specific docs when behavior, contracts, setup, deployment, database, or design rules change.
8. Update `.codex/TASK_CONTEXT.md` after meaningful changes.

## Important Project Documents

- `docs/architecture.md` - system structure, components, boundaries, and data flow
- `docs/development.md` - local setup, run commands, environment variables, tooling
- `docs/domain.md` - business concepts, domain rules, states, and terminology
- `docs/testing.md` - testing strategy, validation rules, and test commands
- `docs/decisions.md` - technical decisions and reasoning
- `docs/workflows.md` - development workflow, branching, review, release process
- `docs/API_CONTRACT.md` - backend API contracts, routes, request/response shapes, status codes, validation, and errors
- `docs/DATABASE.md` - database ownership, connection model, schema, indexes, retention, and failure behavior
- `docs/DEPLOYMENT.md` - container model, runtime ports, environment variables, device mounts, release steps, and smoke checks
- `docs/DESIGN.md` - frontend UI library usage, layout rules, component conventions, accessibility, and responsive behavior
- `docs/IMPLEMENTATION_PLAN.md` - phased implementation tracking, completed milestones, current gaps, and follow-ups
- `.codex/context-map.md` - quick navigation map for agents
- `.codex/review-checklist.md` - checklist before finishing a task
- `.codex/task-template.md` - reusable task prompt template
- `.codex/TASK_CONTEXT.md` - rolling agent memory with current state, recent meaningful changes, validation, issues, and next steps

## Project-Specific Rules to Capture

- API route prefix is `/api`; do not add routes outside the prefix unless explicitly required and documented in `docs/API_CONTRACT.md`.
- Authentication is not implemented. Treat the API as trusted-network only until auth is added and documented.
- Sensor domain logic belongs in backend sensor drivers and service modules, not in frontend components.
- Database access belongs in `Backend/app/db.py` unless a deliberate persistence refactor is documented.
- Sampling thresholds, retention behavior, and history parsing are domain rules; keep them centralized in backend services/utilities.
- Frontend API calls belong under `Frontend/src/api/` where practical.
- Frontend design uses Vue, Naive UI, Chart.js, and local CSS; do not introduce another UI library without a decision entry.
- Real env files and secrets must stay uncommitted.
- No migration or seed system exists; schema is currently created by backend startup.
- Deployment target is Raspberry Pi with Docker, GHCR backend image, local SQLite storage, and hardware device mounts.
- Background sampler, flusher, retention, and SSE tasks run inside the single backend process.

## General Coding Rules

- Keep business logic out of UI components where possible.
- Keep data access separated from business logic where possible.
- Prefer explicit types, models, and clear function boundaries.
- Avoid duplicating domain rules across multiple layers.
- Prefer readable code over clever code.
- Keep functions and modules focused on one responsibility.
- Handle errors explicitly when the user or system can reasonably recover.
- Do not remove existing validation unless there is a clear reason.
- Do not silently ignore failed operations.
- Keep sensor I/O out of request handlers. Sensor reads should stay in drivers and sampler services.
- Keep frontend API calls in `Frontend/src/api/` where practical.

## Validation Commands

Use the commands below when relevant.

```bash
# Backend syntax check
cd Backend
python -m compileall app
```

```bash
# Backend local run, requires hardware and Backend/airmetrics.env
cd Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
# Backend Docker run on Raspberry Pi target
cd Backend
docker compose up --build -d
```

```bash
# Backend smoke checks
curl http://localhost:8000/api/health/live
curl http://localhost:8000/api/health/ready
curl 'http://localhost:8000/api/history?since=24h'
curl -N http://localhost:8000/api/stream
```

```bash
# Frontend install and build
cd Frontend
npm install
npm run build
```

```bash
# Frontend development server
cd Frontend
npm run dev
```

## Documentation Update Rules

Update documentation only when the behavior, structure, setup, contract, deployment model, database behavior, design rules, testing strategy, workflow, or technical decision actually changes.

Do not update documentation for purely cosmetic changes unless the documentation becomes inaccurate.

## Output Expectations

At the end of each task, provide a concise summary:

- Changed files
- What changed
- Validation performed
- Known risks or assumptions

Keep the summary short and practical.
