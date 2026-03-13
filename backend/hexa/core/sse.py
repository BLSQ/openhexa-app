import json

from django.http import StreamingHttpResponse

POLL_INTERVAL = 0.3  # seconds between DB polls
PING_INTERVAL = 10  # seconds between keepalive pings
MAX_DURATION = 1800  # 30 minutes — safety cap for stuck runs


def format_sse(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


def sse_response(generator) -> StreamingHttpResponse:
    response = StreamingHttpResponse(generator, content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
