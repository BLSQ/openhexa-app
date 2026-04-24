import asyncio
import contextlib
import json
from typing import TypedDict

from django.http import StreamingHttpResponse

POLL_INTERVAL = 2  # seconds between DB polls
PING_INTERVAL = 10  # seconds between keepalive pings
MAX_DURATION = 1800  # 30 minutes — safety cap for stuck runs

_KEEPALIVE_SENTINEL = object()


def format_sse(event_type: str, data: dict | TypedDict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


async def with_keepalive(generator, interval: int = 30):
    """Wrap an async SSE generator, emitting a keepalive event every `interval` seconds
    when the generator is idle. Prevents proxies from closing the connection during
    long-running operations that produce no output.
    """
    queue: asyncio.Queue = asyncio.Queue()

    async def _producer():
        try:
            async for item in generator:
                await queue.put(item)
        finally:
            await queue.put(_KEEPALIVE_SENTINEL)

    producer_task = asyncio.create_task(_producer())
    get_task: asyncio.Task | None = None
    try:
        while True:
            if get_task is None:
                get_task = asyncio.ensure_future(queue.get())

            done, _ = await asyncio.wait({get_task}, timeout=interval)

            if not done:
                yield format_sse("keepalive", {})
                continue

            item = get_task.result()
            get_task = None
            if item is _KEEPALIVE_SENTINEL:
                break
            yield item
    finally:
        if get_task is not None and not get_task.done():
            get_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await get_task
        producer_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await producer_task


def sse_response(generator) -> StreamingHttpResponse:
    response = StreamingHttpResponse(generator, content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
