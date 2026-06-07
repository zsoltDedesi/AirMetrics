# Workflows

## Purpose

This document describes how development work should move through AirMetrics.

Use this file to document branching, commits, pull requests, releases, deployment, and review expectations.

## Development Workflow

Recommended general flow:

```text
1. Understand the task
2. Read AGENTS.md and relevant documentation
3. Inspect existing code
4. Make the smallest reasonable change
5. Run relevant validation
6. Update documentation if needed
7. Summarize changes and risks
```

## Agent Workflow

For non-trivial agent tasks:

```text
1. Read AGENTS.md
2. Read .codex/context-map.md
3. Select only the relevant docs for the task
4. Inspect existing source files before editing
5. Keep the change small and consistent with existing patterns
6. Run validation from docs/testing.md
7. Update project-specific docs if contracts or operational rules change
8. Update .codex/TASK_CONTEXT.md after meaningful changes
```

## Branching

Branch naming convention:

```text
feature/short-description
fix/short-description
refactor/short-description
docs/short-description
```

Examples:

```text
feature/add-sensor-mock-mode
fix/history-since-parser
refactor/extract-sampler-service
docs/update-development-guide
```

## Commit Guidelines

Use short, clear commit messages.

Recommended format:

```text
type: short description
```

Examples:

```text
feat: add sensor mock mode
fix: handle invalid history range
refactor: extract sensor health helpers
docs: update setup instructions
test: add sampler threshold regression test
```

## Pull Request Checklist

Before opening or completing a pull request:

- [ ] The change matches the task.
- [ ] Unrelated files were not modified.
- [ ] Tests were added or updated where useful.
- [ ] Relevant validation commands were run.
- [ ] Documentation was updated if needed.
- [ ] Hardware validation limits are noted when relevant.
- [ ] Risks or assumptions are noted.

## Code Review Focus

Review should check:

- Correctness.
- Simplicity.
- Readability.
- Test coverage or validation notes.
- Error handling.
- Security-sensitive changes.
- Hardware/deployment assumptions.
- Unintended behavior changes.

## Release Workflow

Backend image releases are handled by `.github/workflows/backend-image.yml`.
Frontend image releases are handled by `.github/workflows/frontend-image.yml`.

Backend trigger:

- Push tags matching `backend-v*.*.*`.
- Manual `workflow_dispatch`.

Frontend trigger:

- Push tags matching `frontend-v*.*.*`.
- Manual `workflow_dispatch`.

Published image:

```text
ghcr.io/<repository-owner>/airmetrics-backend
```

Frontend image:

```text
ghcr.io/<repository-owner>/airmetrics-frontend
```

Backend tags:

- `latest`
- the Git tag when triggered by a tag push
- `manual-<short-sha>` when triggered manually

Frontend tags:

- `frontend-latest`
- the Git tag when triggered by a `frontend-v*.*.*` tag push
- `frontend-manual-<short-sha>` when triggered manually

Backend build settings:

- Context: `./Backend`
- Dockerfile: `./Backend/Dockerfile`
- Platform: `linux/arm64`
- Push: enabled
- JavaScript GitHub Actions runtime: uses action major versions that declare Node.js 24.

Frontend build settings:

- Context: `./Frontend`
- Dockerfile: `./Frontend/Dockerfile`
- Platform: `linux/amd64`
- Push: enabled
- Build argument: `VITE_API_BASE_BACKEND_URL=/api`
- JavaScript GitHub Actions runtime: uses action major versions that declare Node.js 24.

Backend release process:

```text
1. Merge approved changes.
2. Run relevant local validation.
3. Create and push a backend version tag.
4. Wait for GitHub Actions to publish the image.
5. Pull and restart the service on the Raspberry Pi.
6. Validate health endpoints and sensor behavior.
7. Monitor container logs.
```

Create and push a backend tag:

```bash
git tag backend-v0.1.0
git push origin backend-v0.1.0
```

Deploy on Raspberry Pi:

```bash
cd Backend
docker compose pull
docker compose up -d
docker compose logs -f backend
```

Manual backend image build:

```text
Run workflow_dispatch from the repository Actions tab.
The generated non-version tag is manual-<short-sha>.
```

Create and push a frontend tag:

```bash
git tag frontend-v0.1.0
git push origin frontend-v0.1.0
```

Deploy frontend on Raspberry Pi:

```bash
cd Frontend
docker compose pull
docker compose up -d
docker compose logs -f frontend
```

Manual frontend image build:

```text
Run workflow_dispatch from the repository Actions tab.
The generated non-version tag is frontend-manual-<short-sha>.
```

## Hotfix Workflow

Use this for urgent production or deployed Raspberry Pi fixes.

```text
1. Identify the deployed issue.
2. Create a focused fix.
3. Validate the fix locally or on target hardware.
4. Release with minimum unrelated change.
5. Document root cause if needed.
6. Add regression test if practical.
```

## Local Backend Docker Workflow

```bash
cd Backend
cp airmetrics.env.example airmetrics.env
# edit airmetrics.env for the target hardware
docker compose up --build -d
docker compose logs -f backend
```

## Local Frontend Workflow

```bash
cd Frontend
npm install
npm run dev
```

The frontend must know where the backend API lives through `VITE_API_BASE_BACKEND_URL`.

## Local Frontend Docker Workflow

```bash
cd Frontend
docker compose up --build -d
docker compose logs -f frontend
```

The frontend container serves the app on port `8080`. Browser `/api` requests are proxied to `BACKEND_UPSTREAM`.

## Documentation Workflow

Update documentation when:

- Setup changes.
- Commands change.
- Architecture changes.
- Domain rules change.
- API contracts change.
- Database behavior changes.
- Deployment rules change.
- Design system rules change.
- Testing strategy changes.
- Workflow or release process changes.
- A significant technical decision is made.

Do not update documentation for unrelated or cosmetic reasons.
