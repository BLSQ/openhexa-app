from unittest.mock import MagicMock


def make_upstream(body: bytes, *, status: int = 200, headers: dict | None = None):
    """Stand-in for the requests.Response that ForgejoClient.stream_file returns.

    Only the attributes serve_webapp touches are populated: the status to
    forward, the headers to copy across, and a single-chunk body iterator.
    """
    upstream = MagicMock()
    upstream.status_code = status
    upstream.headers = {"Content-Length": str(len(body)), **(headers or {})}
    upstream.iter_content.return_value = iter([body])
    upstream.content = body
    return upstream


def read_body(response) -> bytes:
    """Read a response body whether or not it is streamed."""
    if response.streaming:
        return b"".join(response.streaming_content)
    return response.content
