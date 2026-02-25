# syntax=docker/dockerfile:1

# --- Builder Stage ---
FROM python:3.11-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Create a virtual environment in /opt/venv
# This bypasses the PEP 668 "externally-managed-environment" error on Debian Bookworm
RUN python -m venv /opt/venv

# Enable the virtual environment for subsequent commands
ENV PATH="/opt/venv/bin:$PATH"

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into the virtual environment
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Runtime Stage ---
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
    
# Add the virtual environment to PATH in the runtime stage as well
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install runtime dependencies
# libgpiod2 is required for GPIO access on Raspberry Pi
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends libgpiod2; \
    rm -rf /var/lib/apt/lists/*

# Copy the pre-built virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY app /app/app

# Copy example env file (optional for sandbox use)
COPY airmetrics.env.example /app/airmetrics.env.example

EXPOSE 8000

# Start the application using the uvicorn from the virtual environment
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]