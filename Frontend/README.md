# AirMetrics Frontend

Vue 3 + Vite dashboard for the AirMetrics project.

The dashboard uses:

- Naive UI for Vue UI primitives.
- Apache ECharts through `vue-echarts` for history charts.
- Axios for backend API calls.
- Local CSS with Material-style design tokens.

## Development

From `Frontend/`:

```bash
npm install
npm run dev
```

Build and preview:

```bash
npm run build
npm run preview
```

## Backend API (dev setup)

The backend API is served under the `/api` prefix (default backend port: `8000`).

If you run the frontend dev server (Vite) on a different origin than the backend, you typically need one of:

- A dev proxy in `vite.config.js` (recommended), or
- CORS enabled in the backend.

## Project status

The frontend renders live sensor cards, system status, time-range controls, and temperature/humidity history charts from the backend API.
