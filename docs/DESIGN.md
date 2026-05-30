# Design System Documentation

## Purpose

This document defines frontend visual and interaction rules for AirMetrics.

Use it when implementing UI components, layout changes, visual states, or responsive behavior.

## UI Library

Primary UI library:

- Naive UI

Supporting libraries:

- Apache ECharts
- `vue-echarts`
- Local CSS in `Frontend/src/styles/`

Rules:

- Prefer existing Naive UI components before creating custom controls.
- Keep styling consistent with the current Figma-derived dashboard structure.
- Do not introduce a new UI library without a documented decision.
- Keep API access separate from visual components where practical.
- Use Material Design 3 style tokens for shared color and typography values.

## Design Tokens

Token source:

- Material-style CSS custom properties are defined in `Frontend/src/styles/base.css`.
- Color tokens use `--md-sys-color-*` names.
- Typography tokens use `--md-sys-typescale-*` names.
- Shape tokens use `--md-sys-shape-*` names.

Rules:

- New shared colors should be added as Material-style system color tokens before use.
- New font sizes should use `--md-sys-typescale-*` tokens instead of local literal sizes.
- Component-specific CSS should reference tokens with `var(...)` where practical.
- ECharts canvas colors should read the same CSS tokens through a small runtime helper, because canvas rendering cannot rely on normal CSS inheritance.
- Sensor-series colors should map to existing system roles where possible: DS18B20 uses tertiary, AM2302 temperature uses error, and AM2302 humidity uses secondary.

## Layout Rules

- Use the custom dashboard shell in `HomeView.vue` for the primary page layout.
- The top-level layout order is header, metric cards, status strip, history toolbar, history charts, and notice cards.
- Use custom card surfaces for the Figma-derived dashboard panels.
- Keep the dashboard centered with the `.dashboard-shell` max-width rule.
- Avoid fixed widths unless a chart or hardware display state requires them.
- Make responsive behavior predictable before adding dense dashboard sections.

## Typography

| Use Case | Style |
| --- | --- |
| Page title | Root `h1` in `HomeView.vue`. |
| Card title | Compact bold heading inside custom dashboard cards. |
| Chart heading | Compact heading inside the history chart card. |
| Body text | Plain paragraphs inside cards and state panels. |
| Sensor values | Text labels with numeric values and units. |

## Components

| Component Type | Convention |
| --- | --- |
| Sensor card | One card per displayed metric: DS18B20 temperature, AM2302 temperature, AM2302 humidity. |
| Status strip | Six compact system tiles for backend, SSE, retention range, database, cleanup exposure, and AM2302 errors. |
| History toolbar | Segmented `1h` / `6h` / `24h` range selector plus event-based, CSV, and threshold controls. |
| History chart | Chart logic belongs in `LineChartWrapper.vue`; API fetch belongs through `Frontend/src/api/history.js`. |
| Health state | Keep API calls in `Frontend/src/api/health.js` and live stream state in `useSensorStream.js`. |
| Error handling | Use small inline messages for health, stream, and history failures; keep technical details in console logs. |

## Chart Display Rules

- Temperature history charts hide values outside the display range `-40°C` to `85°C`.
- Hidden temperature values are treated as visual outliers only; backend history data is not changed.
- When temperature outliers are hidden, show an inline chart badge with the number of hidden points.
- Use ECharts `grid.containLabel`, confined tooltips, clipped series, and fixed chart surfaces so chart content stays inside the card.

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
| mobile | Stack header content, metric cards, status tiles, controls, charts, and notices vertically. |
| tablet | Use one-column metric and chart layouts, with status tiles grouped into multiple columns where space allows. |
| desktop | Use a centered 1216px dashboard, three metric cards, six status tiles, and two chart columns. |

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
- ECharts options in chart components
