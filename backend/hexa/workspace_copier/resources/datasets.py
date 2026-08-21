"""Dataset copier: copy every dataset *owned* by the workspace, with its versions.

Only the latest version is copied by default; ``CopyOptions.all_dataset_versions``
copies every version instead. Versions are always created oldest-first and a
version's files are all uploaded before the next version is created, because
``generateDatasetUploadUrl`` / ``createDatasetVersionFile`` reject any version
that is not the dataset's *latest* one (``LOCKED_VERSION``): a version stops
accepting content the moment a newer one exists. The same rule is why a failed
file transfer abandons the whole dataset instead of moving on — see
``_copy_versions``.

Everything goes through raw ``gql()``. The pinned SDK's dataset methods predate
what this needs: ``create_dataset`` doesn't select the new dataset's ``id``
(required to create versions), ``UpdateDatasetInput`` has no
``sharedWithOrganization``, and there are no version/file mutations at all.
"""

import base64
import tempfile
from typing import IO, Any
from urllib.parse import quote

import httpx
from openhexa.graphql.graphql_client.client import Client
from slugify import slugify

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import ProgressReporter
from hexa.workspace_copier.resources.base import ResourceCopier
from hexa.workspace_copier.results import CopyResult, DatasetsResult, format_bytes
from hexa.workspace_copier.transport import GraphQLError, gql

DATASETS_PAGE_SIZE = 50
VERSIONS_PAGE_SIZE = 50
FILES_PAGE_SIZE = 50

FILE_TRANSFER_TIMEOUT = 300
SPOOL_MAX_SIZE = 32 * 1024 * 1024
"""Bytes a file transfer may hold in memory before spilling to a temp file."""

AZURE_MAX_SINGLE_PUT_SIZE = 5000 * 1024 * 1024  # 5 GiB
AZURE_BLOCK_SIZE = 64 * 1024 * 1024  # 64 MiB to keep memory low


LIST_DATASETS_QUERY = """
query ListWorkspaceDatasets($slug: String!, $page: Int!, $perPage: Int!) {
    workspace(slug: $slug) {
        datasets(page: $page, perPage: $perPage) {
            totalPages
            items {
                dataset {
                    id slug name
                    workspace { slug }
                }
            }
        }
    }
}
"""

DATASET_DETAIL_QUERY = """
query DatasetDetail($id: ID!) {
    dataset(id: $id) {
        id slug name description sharedWithOrganization
        latestVersion { id name changelog }
    }
}
"""

DATASET_VERSIONS_QUERY = """
query DatasetVersions($id: ID!, $page: Int!, $perPage: Int!) {
    dataset(id: $id) {
        versions(page: $page, perPage: $perPage) {
            totalPages
            items { id name changelog createdAt }
        }
    }
}
"""

VERSION_FILES_QUERY = """
query DatasetVersionFiles($id: ID!, $page: Int!, $perPage: Int!) {
    datasetVersion(id: $id) {
        files(page: $page, perPage: $perPage) {
            totalPages
            items { id uri filename contentType }
        }
    }
}
"""

CREATE_DATASET_MUTATION = """
mutation CreateDataset($input: CreateDatasetInput!) {
    createDataset(input: $input) {
        success errors
        dataset { id slug }
    }
}
"""

UPDATE_DATASET_MUTATION = """
mutation UpdateDataset($input: UpdateDatasetInput!) {
    updateDataset(input: $input) { success errors }
}
"""

CREATE_VERSION_MUTATION = """
mutation CreateDatasetVersion($input: CreateDatasetVersionInput!) {
    createDatasetVersion(input: $input) {
        success errors
        version { id name }
    }
}
"""

PREPARE_FILE_DOWNLOAD_MUTATION = """
mutation PrepareVersionFileDownload($input: PrepareVersionFileDownloadInput!) {
    prepareVersionFileDownload(input: $input) { success errors downloadUrl }
}
"""

GENERATE_UPLOAD_URL_MUTATION = """
mutation GenerateDatasetUploadUrl($input: GenerateDatasetUploadUrlInput!) {
    generateDatasetUploadUrl(input: $input) { success errors uploadUrl headers }
}
"""

CREATE_VERSION_FILE_MUTATION = """
mutation CreateDatasetVersionFile($input: CreateDatasetVersionFileInput!) {
    createDatasetVersionFile(input: $input) { success errors file { id uri } }
}
"""


class DatasetsCopier(ResourceCopier):
    name = "datasets"
    label = "Datasets (+versions)"
    option_fields = ("all_dataset_versions",)

    def copy(
        self,
        source: Endpoint,
        target: Endpoint,
        result: CopyResult,
        reporter: ProgressReporter,
        *,
        options: CopyOptions = CopyOptions(),
    ) -> None:
        if source.is_remote and target.is_remote:
            self._copy_remote(source, target, result, reporter, options)
        else:
            raise NotImplementedError(
                "LOCAL datasets copy (native ORM clone) is implemented in a later phase"
            )

    def _copy_remote(
        self,
        source: Endpoint,
        target: Endpoint,
        result: CopyResult,
        reporter: ProgressReporter,
        options: CopyOptions,
    ) -> None:
        ds_result = DatasetsResult()
        result.datasets = ds_result

        datasets = _list_source_datasets(source.client, source.slug)
        assignments = _assign_target_names(datasets)
        existing_slugs = _list_target_slugs(target.client, target.slug)

        # One shared client for every presigned download/upload, as in the files
        # copier: it reuses connections across files and carries no auth headers
        # (presigned URLs are self-authenticating and some storage backends
        # reject requests that also send an Authorization header).
        with httpx.Client(timeout=FILE_TRANSFER_TIMEOUT) as http_client:
            for dataset_id, src_slug, target_name, target_slug in assignments:
                if target_slug in existing_slugs:
                    ds_result.skipped.append(src_slug)
                    reporter.info(f"   skipped dataset '{src_slug}' (already exists)")
                    continue
                try:
                    reporter.info(f"   copying dataset '{src_slug}' ...")
                    self._copy_dataset(
                        source,
                        target,
                        dataset_id,
                        target_name,
                        ds_result,
                        reporter,
                        options,
                        http_client,
                    )
                except GraphQLError as exc:
                    # Collect and continue (like the pipelines copier) so one bad
                    # dataset doesn't abort the rest of the copy.
                    ds_result.failed.append(src_slug)
                    ds_result.warnings.append(
                        f"dataset '{src_slug}' could not be copied — handle "
                        f"manually ({exc})."
                    )
                    reporter.warning(f"   FAILED to copy dataset '{src_slug}' ({exc})")

    def _copy_dataset(
        self,
        source: Endpoint,
        target: Endpoint,
        dataset_id: str,
        target_name: str,
        ds_result: DatasetsResult,
        reporter: ProgressReporter,
        options: CopyOptions,
        http_client: httpx.Client,
    ) -> None:
        detail = _fetch_source_detail(source.client, dataset_id)
        versions = _select_versions(
            source.client, dataset_id, detail, options.all_dataset_versions
        )

        target_id, target_slug = _create_on_target(
            target.client, target.slug, detail, target_name
        )
        _apply_sharing(target.client, target_id, detail, ds_result)

        copied = _copy_versions(
            source,
            target,
            dataset_id,
            target_id,
            versions,
            ds_result,
            reporter,
            http_client,
        )
        ds_result.created.append((target_slug, copied))
        reporter.info(f"   created dataset '{target_slug}' ({len(copied)} version(s))")


# ---------------------------------------------------------------------------
# Source fetch
# ---------------------------------------------------------------------------


def _list_source_datasets(source: Client, slug: str) -> list[tuple[str, str, str]]:
    """Return [(dataset_id, slug, name), ...] for datasets *owned* by the workspace.

    ``workspace.datasets`` is a page of *links*, so it also lists datasets merely
    shared with the workspace (via a link or org-wide sharing). Only datasets
    whose owning workspace is this one are ours to copy.
    """
    datasets = []
    page = 1
    while True:
        data = gql(
            source,
            LIST_DATASETS_QUERY,
            {"slug": slug, "page": page, "perPage": DATASETS_PAGE_SIZE},
            "ListWorkspaceDatasets",
        )
        workspace = data["workspace"]
        if workspace is None:
            raise GraphQLError(
                f"source workspace '{slug}' not found while listing datasets"
            )
        page_data = workspace["datasets"]
        for item in page_data["items"]:
            dataset = item["dataset"]
            owner = (dataset.get("workspace") or {}).get("slug")
            if owner == slug:
                datasets.append((str(dataset["id"]), dataset["slug"], dataset["name"]))
        if page >= page_data["totalPages"] or page_data["totalPages"] == 0:
            break
        page += 1
    return datasets


def _assign_target_names(
    datasets: list[tuple[str, str, str]],
) -> list[tuple[str, str, str, str]]:
    """Assign each source dataset a deterministic, clash-free target slug.

    The target server derives a dataset's slug from ``slugify(name)`` and, on a
    clash within the workspace, appends a *random* hex suffix (see
    ``create_dataset_slug`` in datasets/models.py). That randomness makes target
    slugs unpredictable, so — exactly as the pipelines copier does for codes — we
    disambiguate clashing names ourselves, appending " (2)", " (3)", ..., which
    keeps the server on the plain ``slugify(name)`` path.

    Datasets are processed in a stable order (by source slug) so a given dataset
    always receives the same number, hence the same slug, across runs.

    Returns [(dataset_id, src_slug, target_name, target_slug), ...].
    """
    assignments = []
    used_slugs = set()
    for dataset_id, src_slug, name in sorted(datasets, key=lambda d: d[1]):
        target_name = name
        target_slug = slugify(name)
        n = 2
        while target_slug in used_slugs:
            target_name = f"{name} ({n})"
            target_slug = slugify(target_name)
            n += 1
        used_slugs.add(target_slug)
        assignments.append((dataset_id, src_slug, target_name, target_slug))
    return assignments


def _list_target_slugs(target: Client, target_slug: str) -> set[str]:
    """Return the slugs of datasets already owned by the target workspace."""
    return {
        dataset_slug
        for _id, dataset_slug, _name in _list_source_datasets(target, target_slug)
    }


def _fetch_source_detail(source: Client, dataset_id: str) -> dict[str, Any]:
    data = gql(source, DATASET_DETAIL_QUERY, {"id": dataset_id}, "DatasetDetail")
    detail = data["dataset"]
    if detail is None:
        raise GraphQLError(f"source dataset id={dataset_id} disappeared")
    return detail


def _select_versions(
    source: Client,
    dataset_id: str,
    detail: dict[str, Any],
    all_versions: bool,
) -> list[dict[str, Any]]:
    """Return the source versions to copy, oldest first.

    Default is the latest version alone, which is also why the cheap
    ``latestVersion`` field is part of the detail query. A dataset with no
    version at all yields an empty list: it is still created on the target, just
    without any version.
    """
    if not all_versions:
        latest = detail.get("latestVersion")
        return [latest] if latest else []

    versions: list[dict[str, Any]] = []
    page = 1
    while True:
        data = gql(
            source,
            DATASET_VERSIONS_QUERY,
            {"id": dataset_id, "page": page, "perPage": VERSIONS_PAGE_SIZE},
            "DatasetVersions",
        )
        dataset = data["dataset"]
        if dataset is None:
            raise GraphQLError(f"source dataset id={dataset_id} disappeared")
        page_data = dataset["versions"]
        versions.extend(page_data["items"])
        if page >= page_data["totalPages"] or page_data["totalPages"] == 0:
            break
        page += 1
    # `versions` comes back newest-first (DatasetVersion.Meta.ordering); the
    # target only accepts files for its latest version, so replay oldest-first.
    return sorted(versions, key=lambda v: v["createdAt"])


def _list_version_files(source: Client, version_id: str) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    page = 1
    while True:
        data = gql(
            source,
            VERSION_FILES_QUERY,
            {"id": version_id, "page": page, "perPage": FILES_PAGE_SIZE},
            "DatasetVersionFiles",
        )
        version = data["datasetVersion"]
        if version is None:
            raise GraphQLError(f"source dataset version id={version_id} disappeared")
        page_data = version["files"]
        files.extend(page_data["items"])
        if page >= page_data["totalPages"] or page_data["totalPages"] == 0:
            break
        page += 1
    return files


def _relative_uri(file: dict[str, Any], dataset_id: str, version_id: str) -> str:
    """Strip the source's ``{dataset_id}/{version_id}/`` prefix off a file uri.

    The stored uri is absolute within the datasets bucket (see
    ``DatasetVersion.get_full_uri``) and the target rebuilds that prefix from its
    own ids, so it must be handed the relative part. Stripping the prefix rather
    than reading ``filename`` preserves any subdirectory in the uri.
    """
    uri = file["uri"]
    prefix = f"{dataset_id}/{version_id}/"
    if uri.startswith(prefix):
        return uri[len(prefix) :]
    return file["filename"]


# ---------------------------------------------------------------------------
# Target writes
# ---------------------------------------------------------------------------


def _create_on_target(
    target: Client, target_slug: str, detail: dict[str, Any], name: str
) -> tuple[str, str]:
    """Create an empty dataset on the target and return (id, slug).

    ``name`` is the disambiguated name chosen by :func:`_assign_target_names` so
    the server produces a predictable slug; the actual slug is still read back
    from the response as the source of truth.
    """
    input_ = {
        "workspaceSlug": target_slug,
        "name": name,
        "description": detail.get("description") or "",
    }
    data = gql(target, CREATE_DATASET_MUTATION, {"input": input_}, "CreateDataset")
    result = data["createDataset"]
    if not result["success"] or result.get("dataset") is None:
        raise GraphQLError(
            f"createDataset failed for '{detail['slug']}': "
            + ",".join(result.get("errors") or [])
        )
    created = result["dataset"]
    return str(created["id"]), created["slug"]


def _apply_sharing(
    target: Client,
    target_dataset_id: str,
    detail: dict[str, Any],
    ds_result: DatasetsResult,
) -> None:
    """Mirror ``sharedWithOrganization``, which createDataset cannot set.

    A failure here is a warning rather than an error: the dataset and its
    versions are worth keeping even if the sharing flag didn't take.
    """
    if not detail.get("sharedWithOrganization"):
        return
    input_ = {"datasetId": target_dataset_id, "sharedWithOrganization": True}
    data = gql(target, UPDATE_DATASET_MUTATION, {"input": input_}, "UpdateDataset")
    result = data["updateDataset"]
    if not result["success"]:
        ds_result.warnings.append(
            f"dataset '{detail['slug']}' is shared with its organization on the "
            "source but the flag could not be set on the target ("
            + ",".join(result.get("errors") or [])
            + ") — set it manually."
        )


def _create_version(
    target: Client, target_dataset_id: str, version: dict[str, Any]
) -> str:
    """Create one version on the target dataset and return its id."""
    input_ = {
        "datasetId": target_dataset_id,
        "name": version["name"],
        "changelog": version.get("changelog") or "",
    }
    data = gql(
        target, CREATE_VERSION_MUTATION, {"input": input_}, "CreateDatasetVersion"
    )
    result = data["createDatasetVersion"]
    if not result["success"] or result.get("version") is None:
        raise GraphQLError(
            f"createDatasetVersion failed for '{version['name']}': "
            + ",".join(result.get("errors") or [])
        )
    return str(result["version"]["id"])


def _prepare_download(source: Client, file_id: str, uri: str) -> str | None:
    """Return a presigned download URL, or None if the file has no content.

    ``FILE_NOT_UPLOADED`` means the source has a file row whose blob was never
    written (an interrupted upload); there is nothing to transfer, so the caller
    skips it instead of failing the dataset.
    """
    data = gql(
        source,
        PREPARE_FILE_DOWNLOAD_MUTATION,
        {"input": {"fileId": file_id}},
        "PrepareVersionFileDownload",
    )
    result = data["prepareVersionFileDownload"]
    errors = result.get("errors") or []
    if "FILE_NOT_UPLOADED" in errors:
        return None
    if not result["success"] or not result.get("downloadUrl"):
        raise GraphQLError(
            f"prepareVersionFileDownload failed for '{uri}': " + ",".join(errors)
        )
    return result["downloadUrl"]


def _prepare_upload(
    target: Client, target_version_id: str, uri: str, content_type: str
) -> tuple[str, dict[str, str]]:
    data = gql(
        target,
        GENERATE_UPLOAD_URL_MUTATION,
        {
            "input": {
                "versionId": target_version_id,
                "uri": uri,
                "contentType": content_type,
            }
        },
        "GenerateDatasetUploadUrl",
    )
    result = data["generateDatasetUploadUrl"]
    if not result["success"] or not result.get("uploadUrl"):
        raise GraphQLError(
            f"generateDatasetUploadUrl failed for '{uri}': "
            + ",".join(result.get("errors") or [])
        )
    headers = dict(result.get("headers") or {})
    headers.setdefault("Content-Type", content_type)
    return result["uploadUrl"], headers


def _register_uploaded_file(
    target: Client, target_version_id: str, uri: str, content_type: str
) -> None:
    """Record the uploaded blob as a file of the target version.

    Called *after* the bytes are in place, like the web upload flow does: this
    mutation queues sample/metadata generation, which reads the blob.
    """
    data = gql(
        target,
        CREATE_VERSION_FILE_MUTATION,
        {
            "input": {
                "versionId": target_version_id,
                "uri": uri,
                "contentType": content_type,
            }
        },
        "CreateDatasetVersionFile",
    )
    result = data["createDatasetVersionFile"]
    if not result["success"]:
        raise GraphQLError(
            f"createDatasetVersionFile failed for '{uri}': "
            + ",".join(result.get("errors") or [])
        )


def _azure_upload_by_blocks(
    target: Endpoint,
    target_version_id: str,
    uri: str,
    content_type: str,
    upload_url: str,
    buffer: IO[bytes],
    http_client: httpx.Client,
) -> None:
    """Stage ``buffer`` on Azure Blob Storage block by block, then commit the blob."""

    def put(query: str, content: bytes, headers: dict[str, str] | None = None) -> None:
        nonlocal upload_url
        response = http_client.put(
            f"{upload_url}&{query}", content=content, headers=headers or {}
        )
        if response.status_code in (401, 403):
            # Signed URLs expire after an hour, which a multi-gigabyte upload can
            # outlive. A fresh URL points at the same blob, so the blocks staged
            # so far stay valid and only this request has to be replayed.
            upload_url, _ = _prepare_upload(
                target.client, target_version_id, uri, content_type
            )
            response = http_client.put(
                f"{upload_url}&{query}", content=content, headers=headers or {}
            )
        if not response.is_success:
            raise GraphQLError(
                f"upload of '{uri}' ({query}) returned HTTP "
                f"{response.status_code}: {response.text[:500]}"
            )

    block_ids: list[str] = []
    while block := buffer.read(AZURE_BLOCK_SIZE):
        # Block ids must be unique within the blob and all decode to the same length.
        block_id = base64.b64encode(f"{len(block_ids):032d}".encode()).decode()
        put(f"comp=block&blockid={quote(block_id, safe='')}", block)
        block_ids.append(block_id)

    blocks = "".join(f"<Latest>{block_id}</Latest>" for block_id in block_ids)
    put(
        "comp=blocklist",
        f'<?xml version="1.0" encoding="utf-8"?><BlockList>{blocks}</BlockList>'.encode(),
        # The content type of the blob itself, not of this request.
        {"x-ms-blob-content-type": content_type},
    )


def _transfer_file(
    target: Endpoint,
    file: dict[str, Any],
    uri: str,
    target_version_id: str,
    download_url: str,
    http_client: httpx.Client,
) -> int:
    """Stream one file from source storage to target storage, returning its size.

    Dataset files are the largest artefacts in a workspace, so the body is
    spooled (to memory up to :data:`SPOOL_MAX_SIZE`, then to disk) instead of
    being held whole in memory. httpx reads the spooled file in chunks and sets
    ``Content-Length`` from it, which the storage backends require on a
    presigned PUT.
    """
    content_type = file["contentType"] or "application/octet-stream"
    with tempfile.SpooledTemporaryFile(max_size=SPOOL_MAX_SIZE) as buffer:
        with http_client.stream("GET", download_url) as response:
            if not response.is_success:
                response.read()
                raise GraphQLError(
                    f"download of '{uri}' returned HTTP {response.status_code}: "
                    f"{response.text[:500]}"
                )
            for chunk in response.iter_bytes():
                buffer.write(chunk)
        size = buffer.tell()

        upload_url, headers = _prepare_upload(
            target.client, target_version_id, uri, content_type
        )
        buffer.seek(0)
        # upload block by block for very large files (>5GiB) when on Azure
        if headers.get("x-ms-blob-type") and size > AZURE_MAX_SINGLE_PUT_SIZE:
            _azure_upload_by_blocks(
                target,
                target_version_id,
                uri,
                content_type,
                upload_url,
                buffer,
                http_client,
            )
        else:
            response = http_client.put(upload_url, content=buffer, headers=headers)
            if not response.is_success:
                raise GraphQLError(
                    f"upload of '{uri}' returned HTTP {response.status_code}: "
                    f"{response.text[:500]}"
                )

    _register_uploaded_file(target.client, target_version_id, uri, content_type)
    return size


def _copy_versions(
    source: Endpoint,
    target: Endpoint,
    source_dataset_id: str,
    target_dataset_id: str,
    versions: list[dict[str, Any]],
    ds_result: DatasetsResult,
    reporter: ProgressReporter,
    http_client: httpx.Client,
) -> list[str]:
    """Recreate ``versions`` (oldest first) on the target dataset.

    A version's files must all be uploaded before the next version is created:
    creating a version makes it the dataset's latest, which locks the previous
    one out of any further upload. That is also why a failed file transfer
    raises instead of being collected — going on to the next version would seal
    the incomplete one forever, while stopping leaves it as the latest version so
    the missing file can still be uploaded by hand on the target.
    """
    copied: list[str] = []
    for version in versions:
        target_version_id = _create_version(target.client, target_dataset_id, version)
        reporter.info(f"      created version '{version['name']}'")

        for file in _list_version_files(source.client, version["id"]):
            uri = _relative_uri(file, source_dataset_id, version["id"])
            download_url = _prepare_download(source.client, file["id"], uri)
            if download_url is None:
                ds_result.warnings.append(
                    f"file '{uri}' of version '{version['name']}' has no content "
                    "on the source (never uploaded) — skipped."
                )
                reporter.warning(f"      skipped {uri} (no content on source)")
                continue
            try:
                size = _transfer_file(
                    target,
                    file,
                    uri,
                    target_version_id,
                    download_url,
                    http_client,
                )
            except (GraphQLError, httpx.HTTPError) as exc:
                raise GraphQLError(
                    f"file '{uri}' of version '{version['name']}' failed "
                    f"({exc.__class__.__name__}: {exc}); later versions were not "
                    "copied. The target dataset exists but is incomplete: upload "
                    "the missing file while that version is still the latest one, "
                    "or delete the dataset on the target and re-run"
                ) from exc
            ds_result.files_copied += 1
            ds_result.bytes_copied += size
            reporter.info(f"      copied {uri} ({format_bytes(size)})")

        copied.append(version["name"])
    return copied
