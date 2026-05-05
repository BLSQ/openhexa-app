import datetime
import json


def graphql_datetime_format(dt: datetime.datetime):
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_sse_stream(content: bytes | str) -> list[dict]:
    if isinstance(content, bytes):
        content = content.decode()
    events = []
    current: dict = {}
    for line in content.splitlines():
        if line.startswith("event:"):
            current["event"] = line[len("event:") :].strip()
        elif line.startswith("data:"):
            current["data"] = json.loads(line[len("data:") :].strip())
        elif not line and current:
            events.append(current)
            current = {}
    return events


async def collect_async_stream(streaming_content) -> bytes:
    chunks = []
    async for chunk in streaming_content:
        chunks.append(chunk)
    return b"".join(chunks)
