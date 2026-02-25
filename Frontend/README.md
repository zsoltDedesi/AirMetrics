# AirMetrics Frontend (Vue 3 + Vite)

Vue 3 + Vite frontend for the AirMetrics project.

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

The frontend is currently a scaffold (Vite + Vue starter). Replace `src/components/HelloWorld.vue` and wire it to the backend endpoints as needed.
