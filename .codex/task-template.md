# Agent Task Template

Use this template when giving tasks to an AI coding agent.

## Basic Task Prompt

```text
Read AGENTS.md first.
Then read .codex/context-map.md.
Then inspect the relevant documentation and source files.

Task:
Describe the requested change here.

Constraints:
- Keep the change focused.
- Do not rewrite unrelated code.
- Follow existing project structure and style.
- Update documentation only if behavior, setup, architecture, domain rules, API contracts, database behavior, deployment rules, design rules, workflow, or testing strategy change.
- Update .codex/TASK_CONTEXT.md after meaningful changes.

Validation:
- Run relevant validation commands from docs/testing.md if possible.
- If validation cannot be run, explain why.

Final response:
- Changed files
- What changed
- Validation performed
- Known risks or assumptions
```

## Feature Task Prompt

```text
Read AGENTS.md first.
Then inspect:
- .codex/context-map.md
- docs/architecture.md
- docs/domain.md
- docs/testing.md
- relevant project-specific docs
- relevant source files

Implement the following feature:
[describe feature]

Requirements:
- [requirement 1]
- [requirement 2]
- [requirement 3]

Constraints:
- Keep the implementation minimal and consistent with existing patterns.
- Do not introduce new dependencies unless necessary.
- Do not change unrelated behavior.
- Update docs/domain.md if domain rules change.
- Update docs/architecture.md if component boundaries or data flow change.
- Update docs/API_CONTRACT.md if endpoint behavior changes.
- Update docs/DATABASE.md if persistence behavior changes.
- Update docs/DEPLOYMENT.md if runtime behavior changes.
- Update docs/DESIGN.md if UI rules change.
- Update docs/decisions.md if a significant technical decision is introduced.
- Update .codex/TASK_CONTEXT.md after meaningful changes.

Validation:
- Run relevant tests if available.
- Add or update tests if practical.

Final response:
- Changed files
- What changed
- Validation performed
- Known risks or assumptions
```

## Bug Fix Task Prompt

```text
Read AGENTS.md first.
Then inspect:
- .codex/context-map.md
- the reported error or failing behavior
- related source files
- related tests
- docs/testing.md
- .codex/TASK_CONTEXT.md if it exists

Fix the following bug:
[describe bug]

Expected behavior:
[describe expected behavior]

Current behavior:
[describe current behavior]

Constraints:
- Make the smallest safe fix.
- Do not refactor unrelated code.
- Add a regression test if practical.
- Do not hide errors silently.
- Update project-specific docs if the fix changes behavior, contract, or operational rules.
- Update .codex/TASK_CONTEXT.md after meaningful changes.

Validation:
- Reproduce the issue if possible.
- Confirm the issue is fixed.
- Run relevant tests if available.

Final response:
- Root cause
- Changed files
- What changed
- Validation performed
- Known risks or assumptions
```

## Refactor Task Prompt

```text
Read AGENTS.md first.
Then inspect:
- .codex/context-map.md
- docs/architecture.md
- relevant source files
- related tests
- relevant project-specific docs if contracts may be affected

Refactor the following area:
[describe area]

Goal:
[describe why the refactor is needed]

Constraints:
- Preserve existing behavior.
- Do not change public APIs unless explicitly requested.
- Keep the refactor incremental.
- Avoid large rewrites.
- Update docs/architecture.md if structure changes.
- Update docs/API_CONTRACT.md if API behavior changes.
- Update docs/DATABASE.md if persistence behavior changes.
- Update .codex/TASK_CONTEXT.md after meaningful changes.

Validation:
- Run existing tests.
- If tests are missing, describe manual validation.

Final response:
- Changed files
- What changed
- Behavior changes, if any
- Validation performed
- Known risks or assumptions
```

## Documentation Task Prompt

```text
Read AGENTS.md first.
Then inspect the relevant documentation and source files.

Update documentation for:
[describe topic]

Constraints:
- Keep the documentation practical.
- Do not add speculative information.
- Do not document behavior that is not present in the code.
- Keep examples short and useful.
- Use generic docs for reusable knowledge.
- Use project-specific docs for hard contracts and operational reality.

Final response:
- Changed files
- What changed
- Any assumptions
```

## Review Task Prompt

```text
Read AGENTS.md first.
Then inspect the relevant files.

Review the following change:
[describe change or provide diff]

Focus on:
- correctness
- architecture fit
- readability
- test coverage
- error handling
- security-sensitive changes
- unintended side effects
- documentation consistency

Do not modify files unless explicitly requested.

Final response:
- Critical issues
- Suggested improvements
- Optional improvements
- What looks good
```
