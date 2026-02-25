"""Streaming endpoint that serves live sensor readings over Server-Sent Events."""


from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.stream import SseEvent, SseHub, format_sse, sse_iterator

router = APIRouter()


@router.get("/stream")
async def api_stream(request: Request):
    hub: SseHub = request.app.state.hub
    queue = await hub.subscribe()

    async def event_gen():
        try:
            # Send a snapshot on first subscribe
            for sampler in request.app.state.sampler.values():
                latest = sampler.last_reading
                if latest is not None:
                    yield format_sse(SseEvent(event="reading", data=latest.model_dump()))

            async for chunk in sse_iterator(queue):
                yield chunk
        finally:
            await hub.unsubscribe(queue)

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # in case of nginx reverse proxy, disable response buffering
    }

    return StreamingResponse(event_gen(), media_type="text/event-stream", headers=headers)
