import gzip
import io
from unittest.mock import MagicMock

import requests
import urllib3


def make_upstream(body: bytes, *, status: int = 200, headers: dict | None = None):
    """Stand-in for the requests.Response that ForgejoClient.stream_file returns.

    Only the attributes serve_webapp touches are populated: the status to
    forward, the headers to copy across, and a single-chunk body iterator.
    """
    upstream = MagicMock()
    upstream.status_code = status
    upstream.headers = {"Content-Length": str(len(body)), **(headers or {})}
    upstream.raw.stream.return_value = iter([body])
    upstream.content = body
    return upstream


def make_gzipped_upstream(
    body: bytes, *, status: int = 200, headers: dict | None = None
):
    """A real streaming requests.Response carrying a gzip-encoded body.

    Has to be the genuine class rather than a mock: the point of the tests using
    it is that requests must not transparently decompress the body on the way
    through, which a mock could not demonstrate.
    """
    # mtime=0 keeps the bytes reproducible so a test can assert on them.
    compressed = gzip.compress(body, mtime=0)
    raw = urllib3.HTTPResponse(
        body=io.BytesIO(compressed),
        headers={
            "Content-Encoding": "gzip",
            "Content-Length": str(len(compressed)),
            **(headers or {}),
        },
        status=status,
        preload_content=False,
    )
    upstream = requests.Response()
    upstream.raw = raw
    upstream.status_code = status
    upstream.headers.update(raw.headers)
    return upstream


def read_body(response) -> bytes:
    """Read a response body whether or not it is streamed."""
    if response.streaming:
        return b"".join(response.streaming_content)
    return response.content
