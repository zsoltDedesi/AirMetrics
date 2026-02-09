from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/sensors/{sensor_name}/latest")
async def get_latest(sensor_name: str, request: Request):
    samplers = request.app.state.sampler
    if sensor_name not in samplers:
        raise HTTPException(status_code=404, detail=f"Sensor '{sensor_name}' not found")
    
    latest = samplers[sensor_name].last_reading
    if latest is None:
        raise HTTPException(status_code=404, detail=f"No readings for sensor '{sensor_name}' yet")
    
    return latest
