"""Workspace file transfer: list / download / upload, plus full bucket copy.

Both mediums currently go over GraphQL (presigned download/upload URLs), so a
LOCAL endpoint must still carry a GraphQL ``client`` pointing at its own server.
Native same-server file copy is a deferred follow-up (see the implementation
plan); until then both LOCAL and REMOTE endpoints use the client here.
"""

from collections.abc import Callable, Iterator
from typing import Any

import httpx
from openhexa.graphql.graphql_client.client import Client

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.progress import ProgressReporter
from hexa.workspace_copier.resources.base import ResourceCopier
from hexa.workspace_copier.results import CopyResult, FilesResult
from hexa.workspace_copier.transport import GraphQLError, gql

OBJECTS_PAGE_SIZE = 100

# Directory names whose contents are never worth copying (editor/runtime
# scratch dirs). Matched against any segment of an object key, so a nested
# ``notebooks/.ipynb_checkpoints/foo.ipynb`` is skipped too.
SKIPPED_DIRECTORIES = frozenset({".ipynb_checkpoints", "cache", ".cache"})


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
    source: Client, ws_slug: str, file_path: str, http_client: httpx.Client
) -> bytes:
    """Download a file from the source workspace via a presigned URL."""
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
    resp = http_client.get(url)
    if not resp.is_success:
        raise GraphQLError(
            f"download of '{file_path}' returned HTTP {resp.status_code}: "
            f"{resp.text[:500]}"
        )
    return resp.content


def upload(
    target: Client,
    ws_slug: str,
    file_path: str,
    content: bytes,
    http_client: httpx.Client,
    content_type: str = "application/octet-stream",
) -> None:
    """Upload bytes to the target workspace at the given object key."""
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

    def __init__(
        self,
        skip_existing: bool = False,
        http_client_factory: Callable[[], httpx.Client] | None = None,
    ):
        self.skip_existing = skip_existing
        # The presigned download/upload traffic gets its own bare client (no auth
        # headers — see the comment in copy()). Tests inject a factory returning a
        # WSGI-transport client so those presigned URLs, served by the same
        # in-process app, are reachable without sockets.
        self.http_client_factory = http_client_factory or (
            lambda: httpx.Client(timeout=300)
        )

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
    ) -> None:
        files_result = FilesResult()
        result.files = files_result

        existing = (
            self._existing_on_target(target, reporter) if self.skip_existing else {}
        )

        # One shared client for all presigned download/upload requests so the
        # connection pool reuses TLS handshakes across files instead of paying
        # one per file. It carries no auth headers: presigned URLs are
        # self-authenticating and some storage backends reject requests that
        # also send an Authorization header.
        with self.http_client_factory() as http_client:
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
                # Announce the start so a slow transfer is visible as
                # in-progress instead of looking like a hang.
                reporter.info(f"   [{count}] copying {path} ({obj['size']} bytes) ...")
                try:
                    content = download(source.client, source.slug, path, http_client)
                    upload(target.client, target.slug, path, content, http_client)
                    files_result.copied.append((path, len(content)))
                    reporter.info(f"   [{count}] copied {path} ({len(content)} bytes)")
                except (GraphQLError, httpx.HTTPError) as exc:
                    # Both presigned download/upload (httpx) and the prepare
                    # mutations (GraphQL) can fail per-file. The path and reason
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
