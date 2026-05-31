# syntax=docker/dockerfile:1

# --- Builder Stage ---
FROM node:24-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG VITE_API_BASE_BACKEND_URL=/api
ENV VITE_API_BASE_BACKEND_URL=${VITE_API_BASE_BACKEND_URL}

RUN npm run build

# --- Runtime Stage ---
FROM nginx:1.27-alpine AS runtime

ENV BACKEND_UPSTREAM=http://127.0.0.1:8000

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
  CMD wget -qO- http://127.0.0.1:8080/ >/dev/null || exit 1
