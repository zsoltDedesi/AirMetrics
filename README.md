# AirMetrics

## Backend Docker

### Prerequisites on Raspberry Pi host

- Enable 1-Wire and load `w1-gpio` and `w1-therm`.
- Ensure `/var/lib/airmetrics` exists and is writable by Docker.
- Ensure GPIO devices are available (for AM2302): `/dev/gpiomem`, `/dev/gpiochip0`.

### Build and run

```bash
cd Backend
docker compose up --build -d
```

### Health check

```bash
curl http://localhost:8000/api/health
```
