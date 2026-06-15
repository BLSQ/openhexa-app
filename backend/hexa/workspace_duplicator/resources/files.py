"""Workspace file transfer: list / download / upload, plus full bucket copy.

Both mediums currently go over GraphQL (presigned download/upload URLs), so a
LOCAL endpoint must still carry a GraphQL ``client`` pointing at its own server.
Native same-server file copy is a deferred follow-up (see the implementation
plan); until then both LOCAL and REMOTE endpoints use the client here.
"""

import sys
from collections.abc import Iterator
from typing import Any

import httpx
from openhexa.graphql.graphql_client.client import Client

from hexa.workspace_duplicator.endpoints import Endpoint
from hexa.workspace_duplicator.resources.base import ResourceCopier
from hexa.workspace_duplicator.results import DuplicationResult, FilesResult
from hexa.workspace_duplicator.transport import GraphQLError, _dbg, gql

OBJECTS_PAGE_SIZE = 100


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


def download(source: Client, ws_slug: str, file_path: str) -> bytes:
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
    _dbg(f"download {file_path} <- {url}")
    with httpx.Client(timeout=300) as c:
        resp = c.get(url)
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
    _dbg(f"upload {file_path} ({len(content)} bytes) -> {url}")
    with httpx.Client(timeout=300) as c:
        resp = c.put(url, content=content, headers=headers)
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

    def copy(
        self, source: Endpoint, target: Endpoint, result: DuplicationResult
    ) -> None:
        files_result = FilesResult()
        result.files = files_result

        print("=> Listing source files ...")
        for obj in walk(source.client, source.slug):
            path = obj["key"]
            size = obj.get("size") or 0
            try:
                print(f"   - copying '{path}' ({size} bytes) ...")
                content = download(source.client, source.slug, path)
                upload(target.client, target.slug, path, content)
                files_result.copied.append((path, len(content)))
            except GraphQLError:
                # Surface the failure in the live log without dumping the (often
                # HTML) server response. The full path goes into failed for the
                # final summary so the user can re-attempt manually.
                print(f"\tFAILED to copy '{path}'", file=sys.stderr)
                files_result.failed.append(path)
