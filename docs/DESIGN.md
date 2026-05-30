# Design System Documentation

## Purpose

This document defines frontend visual and interaction rules for AirMetrics.

Use it when implementing UI components, layout changes, visual states, or responsive behavior.

## UI Library

Primary UI library:

- Naive UI

Supporting libraries:

- Chart.js
- `vue-chart-3`
- Local CSS in `Frontend/src/styles/`

Rules:

- Prefer existing Naive UI components before creating custom controls.
- Keep styling consistent with the current dashboard structure.
- Do not introduce a new UI library without a documented decision.
- Keep API access separate from visual components where practical.

## Layout Rules

- Use `n-space` for simple vertical or horizontal spacing in the current dashboard.
- Use `n-card` for individual sensor, chart, and health panels.
- Keep the dashboard centered through the existing `#app` max-width rule.
- Avoid fixed widths unless a chart or hardware display state requires them.
- Make responsive behavior predictable before adding dense dashboard sections.

## Typography

| Use Case | Style |
| --- | --- |
| Page title | Root `h1` in `HomeView.vue`. |
| Card title | Naive UI `n-card` title prop. |
| Chart heading | Compact heading inside the history card. |
| Body text | Plain paragraphs inside cards. |
| Sensor values | Text labels with numeric values and units. |

## Components

| Component Type | Convention |
| --- | --- |
| Sensor card | One card per sensor with latest available values and units. |
| History chart | Chart logic belongs in `LineChartWrapper.vue`; API fetch belongs through `Frontend/src/api/history.js`. |
| Health action | Use a Naive UI button and keep API calls in `Frontend/src/api/health.js`. |
| Error handling | Use small inline messages for health, stream, and history failures; keep technical details in console logs. |

## Accessibility

- Interactive elements must be keyboard reachable.
- Buttons should have clear visible labels.
- Sensor values should include units.
- Color should not be the only way to communicate state.
- Chart information should not be the only place critical sensor values appear.

## Responsive Behavior

Breakpoints are not formally defined yet.

| Size | Behavior |
| --- | --- |
| mobile | Keep cards stacked vertically. |
| tablet | Keep stacked layout unless chart readability requires adjustment. |
| desktop | Use centered dashboard with constrained max width. |

## Frontend API Error Handling

Current behavior:

- Health errors are logged and shown as an inline dashboard message.
- History fetch errors are logged and shown as an inline chart message.
- SSE errors are logged through state and shown as an inline stream message.

Rules for future changes:

- Keep API helpers under `Frontend/src/api/`.
- Show user-visible errors for actions that users can recover from.
- Avoid silent failures for backend connectivity issues.
- Close `EventSource` on component unmount.

## Design Ownership

Design rules are currently defined in:

- `Frontend/src/styles/base.css`
- `Frontend/src/styles/style.css`
- `Frontend/src/styles/index.css`
- `Frontend/src/composables/`
- `Frontend/src/utils/`
- Naive UI component usage in Vue files
- Chart.js options in chart components
