# Agent Review Checklist

## Before Editing

- [ ] I read `AGENTS.md`.
- [ ] I read `.codex/context-map.md`.
- [ ] I identified the relevant documentation.
- [ ] I inspected the existing implementation.
- [ ] I understand the requested change.
- [ ] I avoided unrelated changes.

## During Implementation

- [ ] The change is focused.
- [ ] Existing structure and style are followed.
- [ ] Naming is consistent with the project.
- [ ] Business logic is placed in the correct layer.
- [ ] Database access is placed in the correct layer.
- [ ] Computed/domain logic is centralized where required.
- [ ] Sensor I/O stays out of request handlers.
- [ ] Frontend API calls stay in `Frontend/src/api/` where practical.
- [ ] Frontend API error handling follows project conventions.
- [ ] Error handling is explicit.
- [ ] No secrets or local-only values are committed.
- [ ] No generated files were edited unnecessarily.

## Testing and Validation

- [ ] Relevant tests or validation commands were run, if available.
- [ ] New tests were added or updated, if useful.
- [ ] Manual validation was performed when needed.
- [ ] Hardware validation limits were noted when relevant.
- [ ] Edge cases were considered.
- [ ] Existing behavior was not accidentally removed.
- [ ] Backend validation was considered.
- [ ] Frontend validation was considered.
- [ ] Database validation was considered.
- [ ] Docker validation was considered when relevant.
- [ ] Security/audit checks were considered when relevant.

## Documentation

- [ ] `docs/architecture.md` was updated if architecture changed.
- [ ] `docs/development.md` was updated if setup or commands changed.
- [ ] `docs/domain.md` was updated if domain rules changed.
- [ ] `docs/testing.md` was updated if testing strategy changed.
- [ ] `docs/workflows.md` was updated if workflow or release process changed.
- [ ] `docs/decisions.md` was updated if a significant decision was made.
- [ ] `docs/API_CONTRACT.md` was updated if API contracts changed.
- [ ] `docs/DATABASE.md` was updated if database behavior changed.
- [ ] `docs/DEPLOYMENT.md` was updated if deployment changed.
- [ ] `docs/DESIGN.md` was updated if design rules changed.
- [ ] `docs/IMPLEMENTATION_PLAN.md` was updated if implementation status changed.
- [ ] `.codex/TASK_CONTEXT.md` was updated after meaningful changes.

## Final Response

The final response should include:

- [ ] Changed files.
- [ ] What changed.
- [ ] Validation performed.
- [ ] Known risks or assumptions.
- [ ] Suggested follow-up only if useful.
