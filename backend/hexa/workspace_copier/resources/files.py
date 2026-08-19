"""Workspace file transfer: list / download / upload, plus full bucket copy.

Both mediums currently go over GraphQL (presigned download/upload URLs), so a
LOCAL endpoint must still carry a GraphQL ``client`` pointing at its own server.
Native same-server file copy is a deferred follow-up (see the implementation
plan); until then both LOCAL and REMOTE endpoints use the client here.
"""

import tempfile
from collections.abc import Iterator
from typing import IO, Any

import httpx
from openhexa.graphql.graphql_client.client import Client

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import ProgressReporter
from hexa.workspace_copier.resources.base import ResourceCopier
from hexa.workspace_copier.results import CopyResult, FilesResult, format_bytes
from hexa.workspace_copier.transport import GraphQLError, gql

OBJECTS_PAGE_SIZE = 100

# Bytes moved per read/write while streaming a file through the spool.
CHUNK_SIZE = 4 * 1024 * 1024

# A presigned PUT is a single-part upload, which S3 caps at 5 GiB. Anything
# bigger needs multipart, which the presigned-URL flow cannot express — so
# reject it up front instead of spending minutes discovering it mid-transfer.
MAX_UPLOAD_SIZE = 5 * 1024**3

# Per-operation, not per-file: with a streamed transfer, `read` and `write`
# bound the wait for a single chunk, so a stalled connection fails in a couple
# of minutes instead of tying up the transfer for the length of a whole file.
TRANSFER_TIMEOUT = httpx.Timeout(connect=30.0, read=120.0, write=120.0, pool=30.0)

# Directory names whose contents are never worth copying (editor/runtime
# scratch dirs). Matched against any segment of an object key, so a nested
# ``notebooks/.ipynb_checkpoints/foo.ipynb`` is skipped too.
SKIPPED_DIRECTORIES = frozenset({".ipynb_checkpoints", ".cache"})


def is_skipped(key: str) -> bool:
    """Whether an object key lives under a skipped directory."""
    return any(segment in SKIPPED_DIRECTORIES for segment in key.split("/"))


PREPARE_DOWNLOAD_MUTATION = """
mutation PrepareDownload($input: PrepareObjectDownloadInput!) {
    prepareObjectDownload(input: $input) {
        success errors downloadUrl
    }
}
"""

PREPARE_UPLOAD_MUTATION = """
mutation PrepareUpload($input: PrepareObjectUploadInput!) {
    prepareObjectUpload(input: $input) {
        success errors uploadUrl headers
    }
}
"""

LIST_OBJECTS_QUERY = """
query ListObjects($slug: String!, $prefix: String, $page: Int!, $perPage: Int!) {
    workspace(slug: $slug) {
        bucket {
            objects(prefix: $prefix, page: $page, perPage: $perPage, ignoreHiddenFiles: false) {
                hasNextPage
                items {
                    key name path size type
                }
            }
        }
    }
}
"""


def download(
    source: Client,
    ws_slug: str,
    file_path: str,
    http_client: httpx.Client,
    destination: IO[bytes],
) -> int:
    """Stream a source file into `destination`, returning the bytes written.

    Streamed into a caller-owned buffer rather than returned as bytes: buckets
    hold multi-GB objects, and holding one whole file in memory (twice over,
    since ``Response.content`` joins the accumulated chunks into a second
    copy) is what got the process OOM-killed on large workspaces.
    """
    data = gql(
        source,
        PREPARE_DOWNLOAD_MUTATION,
        {
            "input": {
                "workspaceSlug": ws_slug,
                "objectKey": file_path,
                "forceAttachment": False,
            }
        },
        "PrepareDownload",
    )
    result = data["prepareObjectDownload"]
    if not result["success"] or not result.get("downloadUrl"):
        raise GraphQLError(
            f"prepareObjectDownload failed for '{file_path}': "
            + ",".join(result.get("errors") or [])
        )
    url = result["downloadUrl"]
    written = 0
    with http_client.stream("GET", url) as resp:
        if not resp.is_success:
            # The body of a streamed response is not available until read.
            resp.read()
            raise GraphQLError(
                f"download of '{file_path}' returned HTTP {resp.status_code}: "
                f"{resp.text[:500]}"
            )
        for chunk in resp.iter_bytes(CHUNK_SIZE):
            written += destination.write(chunk)
    return written


def upload(
    target: Client,
    ws_slug: str,
    file_path: str,
    content: IO[bytes],
    http_client: httpx.Client,
    content_type: str = "application/octet-stream",
) -> None:
    """Upload an open binary stream to the target workspace at the given key.

    `content` is read from its current position. httpx derives Content-Length
    from the file descriptor, which matters: without a known length it would
    fall back to chunked transfer encoding, and presigned PUT endpoints reject
    that.
    """
    data = gql(
        target,
        PREPARE_UPLOAD_MUTATION,
        {
            "input": {
                "workspaceSlug": ws_slug,
                "objectKey": file_path,
                "contentType": content_type,
            }
        },
        "PrepareUpload",
    )
    result = data["prepareObjectUpload"]
    if not result["success"] or not result.get("uploadUrl"):
        raise GraphQLError(
            f"prepareObjectUpload failed for '{file_path}': "
            + ",".join(result.get("errors") or [])
        )
    url = result["uploadUrl"]
    headers = dict(result.get("headers") or {})
    headers.setdefault("Content-Type", content_type)
    resp = http_client.put(url, content=content, headers=headers)
    if not resp.is_success:
        raise GraphQLError(
            f"upload of '{file_path}' returned HTTP {resp.status_code}: "
            f"{resp.text[:500]}"
        )


def walk(client: Client, ws_slug: str, prefix: str = "") -> Iterator[dict[str, Any]]:
    """Recursively yield FILE BucketObject dicts under `prefix`.

    The bucket.objects field is delimited (returns DIRECTORY entries rather
    than recursing), so we walk each directory ourselves.
    """
    # Buffer all directory entries at this level so we don't interleave
    # recursive listings with this level's pagination.
    subdirs: list[str] = []
    page = 1
    while True:
        data = gql(
            client,
            LIST_OBJECTS_QUERY,
            {
                "slug": ws_slug,
                "prefix": prefix or None,
                "page": page,
                "perPage": OBJECTS_PAGE_SIZE,
            },
            "ListObjects",
        )
        ws = data["workspace"]
        if ws is None:
            return
        page_data = ws["bucket"]["objects"]
        for obj in page_data["items"]:
            if is_skipped(obj["key"]):
                continue
            if obj["type"] == "FILE":
                yield obj
            elif obj["type"] == "DIRECTORY":
                subdirs.append(obj["key"])
        if not page_data["hasNextPage"]:
            break
        page += 1
    for sub in subdirs:
        yield from walk(client, ws_slug, sub)


class FilesCopier(ResourceCopier):
    name = "files"
    label = "Files (bucket)"

    def _existing_on_target(
        self, target: Endpoint, reporter: ProgressReporter
    ) -> dict[str, int]:
        """List the target bucket up front so re-runs can skip matching files.

        One listing pass is far cheaper than the four round trips a copy costs
        per file. On failure we fall back to copying everything — copies are
        plain overwrites, so that is always safe, just slower.
        """
        try:
            existing = {
                obj["key"]: obj["size"] for obj in walk(target.client, target.slug)
            }
        except (GraphQLError, httpx.HTTPError) as exc:
            reporter.warning(
                f"   could not list target files ({exc}) — copying everything"
            )
            return {}
        if existing:
            reporter.info(
                f"   target already has {len(existing)} file(s); "
                "files matching by key and size will be skipped"
            )
        return existing

    def copy(
        self,
        source: Endpoint,
        target: Endpoint,
        result: CopyResult,
        reporter: ProgressReporter,
        *,
        options: CopyOptions = CopyOptions(),
    ) -> None:
        files_result = FilesResult()
        result.files = files_result

        existing = self._existing_on_target(target, reporter)

        # One shared client for all presigned download/upload requests so the
        # connection pool reuses TLS handshakes across files instead of paying
        # one per file. It carries no auth headers: presigned URLs are
        # self-authenticating and some storage backends reject requests that
        # also send an Authorization header.
        with httpx.Client(timeout=TRANSFER_TIMEOUT) as http_client:
            # walk() is a generator whose paginated/recursive gql() calls can
            # themselves raise (page 2+, a subdir listing). Driving it via
            # next() lets us record a listing failure and keep the files copied
            # so far instead of letting the error escape copy() and lose them.
            walker = walk(source.client, source.slug)
            count = 0
            while True:
                try:
                    obj = next(walker)
                except StopIteration:
                    break
                except (GraphQLError, httpx.HTTPError) as exc:
                    files_result.failed.append(("<listing>", str(exc)))
                    reporter.warning(f"   FAILED to list remaining files: {exc}")
                    break
                count += 1
                path = obj["key"]
                if path in existing and existing[path] == obj["size"]:
                    files_result.skipped += 1
                    reporter.info(
                        f"   [{count}] skipped {path} (already exists, same size)"
                    )
                    continue
                if obj["size"] > MAX_UPLOAD_SIZE:
                    reason = (
                        f"TooLarge: {format_bytes(obj['size'])} exceeds the "
                        f"{format_bytes(MAX_UPLOAD_SIZE)} single-part upload limit"
                    )
                    files_result.failed.append((path, reason))
                    reporter.warning(f"   [{count}] SKIPPED {path}: {reason}")
                    continue
                # Announce the start so a slow transfer is visible as
                # in-progress instead of looking like a hang.
                reporter.info(
                    f"   [{count}] copying {path} ({format_bytes(obj['size'])}) ..."
                )
                try:
                    # Spooled to a temp file so peak memory is one chunk rather
                    # than the whole object. TMPDIR must have room for the
                    # largest file being copied.
                    with tempfile.TemporaryFile() as buffer:
                        size = download(
                            source.client, source.slug, path, http_client, buffer
                        )
                        buffer.seek(0)
                        upload(target.client, target.slug, path, buffer, http_client)
                    files_result.copied.append((path, size))
                    reporter.info(f"   [{count}] copied {path} ({format_bytes(size)})")
                except (GraphQLError, httpx.HTTPError, OSError) as exc:
                    # Both presigned download/upload (httpx) and the prepare
                    # mutations (GraphQL) can fail per-file, as can the spool
                    # itself (OSError, e.g. a full TMPDIR). The path and reason
                    # go into failed for the final summary so the user can see
                    # why and re-attempt it manually.
                    reason = f"{exc.__class__.__name__}: {exc}"
                    files_result.failed.append((path, reason))
                    reporter.warning(f"   [{count}] FAILED to copy {path}: {reason}")

        reporter.info(
            f"   {len(files_result.copied)} file(s) copied, "
            f"{files_result.skipped} skipped, "
            f"{len(files_result.failed)} failed"
        )
