"""Dataset copier: copy the source workspace's *owned* datasets to the target.

REMOTE branch. The source workspace's dataset list also surfaces datasets shared
in from other workspaces/organizations; we keep only the ones whose primary
``workspace`` is the source (owned by it) and skip the rest, so we never
re-create data the source doesn't own.

Each dataset is re-created via ``createDataset`` (the server re-derives the slug
from the name with a collision suffix, so we read the slug back rather than
passing one — same caveat as the workspace/pipeline copiers). Versions are then
recreated **oldest→newest**: dataset version files can only be uploaded to a
dataset's *latest* version (the server returns ``LOCKED_VERSION`` otherwise), and
creating the next version locks the previous one, so each version's files are
uploaded immediately after that version is created.

File bytes move over presigned URLs — ``prepareVersionFileDownload`` on the
source, ``generateDatasetUploadUrl`` + ``createDatasetVersionFile`` on the target
— the same binary-safe path the bucket files copier uses.

The LOCAL (ORM) branch is implemented in a later phase.
"""

from typing import Any

import httpx
from openhexa.graphql.graphql_client.client import Client

from hexa.workspace_duplicator.endpoints import Endpoint
from hexa.workspace_duplicator.resources.base import ResourceCopier
from hexa.workspace_duplicator.results import DatasetsResult, DuplicationResult
from hexa.workspace_duplicator.transport import GraphQLError, _dbg, gql

DATASETS_PAGE_SIZE = 50
VERSIONS_PAGE_SIZE = 50
FILES_PAGE_SIZE = 100


# `workspace.datasets` returns a DatasetLinkPage; each item wraps the dataset and
# its primary `workspace`, which we use to keep only datasets owned by the source.
LIST_WORKSPACE_DATASETS_QUERY = """
query WorkspaceDatasets($slug: String!, $page: Int!, $perPage: Int!) {
    workspace(slug: $slug) {
        datasets(page: $page, perPage: $perPage) {
            totalPages
            items {
                dataset {
                    id slug name description
                    workspace { slug }
                }
            }
        }
    }
}
"""

LIST_DATASET_VERSIONS_QUERY = """
query DatasetVersions($id: ID!, $page: Int!, $perPage: Int!) {
    dataset(id: $id) {
        versions(page: $page, perPage: $perPage) {
            totalPages
            items { id name changelog }
        }
    }
}
"""

LIST_VERSION_FILES_QUERY = """
query DatasetVersionFiles($id: ID!, $page: Int!, $perPage: Int!) {
    datasetVersion(id: $id) {
        files(page: $page, perPage: $perPage) {
            totalPages
            items { id filename contentType }
        }
    }
}
"""

CREATE_DATASET_MUTATION = """
mutation CreateDataset($input: CreateDatasetInput!) {
    createDataset(input: $input) {
        success errors
        dataset { id slug name }
    }
}
"""

CREATE_DATASET_VERSION_MUTATION = """
mutation CreateDatasetVersion($input: CreateDatasetVersionInput!) {
    createDatasetVersion(input: $input) {
        success errors
        version { id name }
    }
}
"""

PREPARE_DOWNLOAD_MUTATION = """
mutation PrepareVersionFileDownload($input: PrepareVersionFileDownloadInput!) {
    prepareVersionFileDownload(input: $input) {
        success errors downloadUrl
    }
}
"""

GENERATE_UPLOAD_URL_MUTATION = """
mutation GenerateDatasetUploadUrl($input: GenerateDatasetUploadUrlInput!) {
    generateDatasetUploadUrl(input: $input) {
        success errors uploadUrl headers
    }
}
"""

CREATE_VERSION_FILE_MUTATION = """
mutation CreateDatasetVersionFile($input: CreateDatasetVersionFileInput!) {
    createDatasetVersionFile(input: $input) {
        success errors
        file { id }
    }
}
"""


class DatasetsCopier(ResourceCopier):
    name = "datasets"
    label = "Datasets (+versions, files)"

    def copy(
        self, source: Endpoint, target: Endpoint, result: DuplicationResult
    ) -> None:
        if source.is_remote and target.is_remote:
            self._copy_remote(source, target, result)
        else:
            raise NotImplementedError(
                "LOCAL datasets copy (native ORM clone) is implemented in a later phase"
            )

    def _copy_remote(
        self, source: Endpoint, target: Endpoint, result: DuplicationResult
    ) -> None:
        ds_result = DatasetsResult()
        result.datasets = ds_result

        existing = _list_workspace_dataset_slugs(target.client, target.slug)

        for dataset in _list_owned_datasets(source.client, source.slug):
            slug = dataset["slug"]
            if slug in existing:
                ds_result.skipped.append(slug)
                continue
            try:
                self._copy_dataset(source, target, dataset, ds_result)
            except GraphQLError:
                # Collect and continue (like the connections copier) so one bad
                # dataset doesn't abort the rest of the migration.
                ds_result.failed.append(slug)

    def _copy_dataset(
        self,
        source: Endpoint,
        target: Endpoint,
        dataset: dict[str, Any],
        ds_result: DatasetsResult,
    ) -> None:
        target_id, target_slug = _create_dataset(target.client, target.slug, dataset)

        version_names: list[str] = []
        for version in _list_versions(source.client, dataset["id"]):
            target_version_id = _create_version(target.client, target_id, version)
            version_names.append(version["name"])
            self._copy_version_files(
                source, target, version, target_version_id, target_slug, ds_result
            )

        ds_result.created.append((target_slug, version_names))

    def _copy_version_files(
        self,
        source: Endpoint,
        target: Endpoint,
        version: dict[str, Any],
        target_version_id: str,
        target_slug: str,
        ds_result: DatasetsResult,
    ) -> None:
        for file in _list_version_files(source.client, version["id"]):
            try:
                content = download(source.client, file["id"])
                upload(
                    target.client,
                    target_version_id,
                    file["filename"],
                    file["contentType"],
                    content,
                )
                ds_result.files_copied += 1
            except GraphQLError:
                # A single bad file is recorded and skipped; the rest of the
                # version (and dataset) still migrate.
                ds_result.warnings.append(
                    f"dataset '{target_slug}' version '{version['name']}' file "
                    f"'{file['filename']}' could not be copied — handle manually."
                )


# ---------------------------------------------------------------------------
# Source reads
# ---------------------------------------------------------------------------


def _list_owned_datasets(client: Client, slug: str) -> list[dict[str, Any]]:
    """Return the datasets owned by (primary workspace ==) the source workspace."""
    owned: list[dict[str, Any]] = []
    page = 1
    while True:
        page_data = _fetch_workspace_datasets_page(client, slug, page)
        if page_data is None:
            raise GraphQLError(
                f"source workspace '{slug}' not found while listing datasets"
            )
        for item in page_data["items"]:
            dataset = item["dataset"]
            owner = dataset.get("workspace")
            if owner and owner["slug"] == slug:
                owned.append(dataset)
        if page >= page_data["totalPages"] or page_data["totalPages"] == 0:
            break
        page += 1
    return owned


def _list_workspace_dataset_slugs(client: Client, slug: str) -> set[str]:
    """Return every dataset slug visible in the workspace (used to skip dupes)."""
    slugs: set[str] = set()
    page = 1
    while True:
        page_data = _fetch_workspace_datasets_page(client, slug, page)
        if page_data is None:
            return slugs
        slugs.update(item["dataset"]["slug"] for item in page_data["items"])
        if page >= page_data["totalPages"] or page_data["totalPages"] == 0:
            break
        page += 1
    return slugs


def _fetch_workspace_datasets_page(
    client: Client, slug: str, page: int
) -> dict[str, Any] | None:
    data = gql(
        client,
        LIST_WORKSPACE_DATASETS_QUERY,
        {"slug": slug, "page": page, "perPage": DATASETS_PAGE_SIZE},
        "WorkspaceDatasets",
    )
    ws = data["workspace"]
    if ws is None:
        return None
    return ws["datasets"]


def _list_versions(client: Client, dataset_id: str) -> list[dict[str, Any]]:
    """Return a dataset's versions oldest→newest across all pages.

    The API returns versions newest-first (model ordering ``-created_at``); we
    reverse so they are recreated oldest-first, which the latest-version upload
    constraint requires.
    """
    versions: list[dict[str, Any]] = []
    page = 1
    while True:
        data = gql(
            client,
            LIST_DATASET_VERSIONS_QUERY,
            {"id": dataset_id, "page": page, "perPage": VERSIONS_PAGE_SIZE},
            "DatasetVersions",
        )
        dataset = data["dataset"]
        if dataset is None:
            raise GraphQLError(
                f"source dataset id={dataset_id} disappeared while listing versions"
            )
        page_data = dataset["versions"]
        versions.extend(page_data["items"])
        if page >= page_data["totalPages"] or page_data["totalPages"] == 0:
            break
        page += 1
    versions.reverse()
    return versions


def _list_version_files(client: Client, version_id: str) -> list[dict[str, Any]]:
    """Return all files of a dataset version across all pages."""
    files: list[dict[str, Any]] = []
    page = 1
    while True:
        data = gql(
            client,
            LIST_VERSION_FILES_QUERY,
            {"id": version_id, "page": page, "perPage": FILES_PAGE_SIZE},
            "DatasetVersionFiles",
        )
        version = data["datasetVersion"]
        if version is None:
            raise GraphQLError(
                f"source dataset version id={version_id} disappeared while "
                "listing files"
            )
        page_data = version["files"]
        files.extend(page_data["items"])
        if page >= page_data["totalPages"] or page_data["totalPages"] == 0:
            break
        page += 1
    return files


def download(client: Client, file_id: str) -> bytes:
    """Download a dataset version file from the source via a presigned URL."""
    data = gql(
        client,
        PREPARE_DOWNLOAD_MUTATION,
        {"input": {"fileId": file_id}},
        "PrepareVersionFileDownload",
    )
    result = data["prepareVersionFileDownload"]
    if not result["success"] or not result.get("downloadUrl"):
        raise GraphQLError(
            f"prepareVersionFileDownload failed for file id={file_id}: "
            + ",".join(result.get("errors") or [])
        )
    url = result["downloadUrl"]
    _dbg(f"download dataset file {file_id} <- {url}")
    with httpx.Client(timeout=300) as c:
        resp = c.get(url)
    if not resp.is_success:
        raise GraphQLError(
            f"download of dataset file id={file_id} returned HTTP "
            f"{resp.status_code}: {resp.text[:500]}"
        )
    return resp.content


# ---------------------------------------------------------------------------
# Target writes
# ---------------------------------------------------------------------------


def _create_dataset(
    client: Client, workspace_slug: str, dataset: dict[str, Any]
) -> tuple[str, str]:
    """Create the dataset on the target, returning (id, server-assigned slug)."""
    data = gql(
        client,
        CREATE_DATASET_MUTATION,
        {
            "input": {
                "workspaceSlug": workspace_slug,
                "name": dataset["name"],
                "description": dataset.get("description") or "",
            }
        },
        "CreateDataset",
    )
    result = data["createDataset"]
    if not result["success"] or result.get("dataset") is None:
        raise GraphQLError(
            f"createDataset failed for '{dataset['slug']}': "
            + ",".join(result.get("errors") or [])
        )
    created = result["dataset"]
    return created["id"], created["slug"]


def _create_version(client: Client, dataset_id: str, version: dict[str, Any]) -> str:
    """Create a version on the target dataset, returning its id."""
    data = gql(
        client,
        CREATE_DATASET_VERSION_MUTATION,
        {
            "input": {
                "datasetId": dataset_id,
                "name": version["name"],
                "changelog": version.get("changelog") or "",
            }
        },
        "CreateDatasetVersion",
    )
    result = data["createDatasetVersion"]
    if not result["success"] or result.get("version") is None:
        raise GraphQLError(
            f"createDatasetVersion failed for version '{version['name']}': "
            + ",".join(result.get("errors") or [])
        )
    return result["version"]["id"]


def upload(
    client: Client,
    version_id: str,
    uri: str,
    content_type: str,
    content: bytes,
) -> None:
    """Upload one file to a target dataset version, then register it.

    ``uri`` is the bare filename; the server prefixes it with the dataset/version
    ids. Uploads only work on the dataset's latest version, so this must be
    called before the next version is created.
    """
    data = gql(
        client,
        GENERATE_UPLOAD_URL_MUTATION,
        {"input": {"versionId": version_id, "uri": uri, "contentType": content_type}},
        "GenerateDatasetUploadUrl",
    )
    result = data["generateDatasetUploadUrl"]
    if not result["success"] or not result.get("uploadUrl"):
        raise GraphQLError(
            f"generateDatasetUploadUrl failed for '{uri}': "
            + ",".join(result.get("errors") or [])
        )
    url = result["uploadUrl"]
    headers = dict(result.get("headers") or {})
    headers.setdefault("Content-Type", content_type)
    _dbg(f"upload dataset file {uri} ({len(content)} bytes) -> {url}")
    with httpx.Client(timeout=300) as c:
        resp = c.put(url, content=content, headers=headers)
    if not resp.is_success:
        raise GraphQLError(
            f"upload of dataset file '{uri}' returned HTTP {resp.status_code}: "
            f"{resp.text[:500]}"
        )

    data = gql(
        client,
        CREATE_VERSION_FILE_MUTATION,
        {"input": {"versionId": version_id, "uri": uri, "contentType": content_type}},
        "CreateDatasetVersionFile",
    )
    result = data["createDatasetVersionFile"]
    if not result["success"]:
        raise GraphQLError(
            f"createDatasetVersionFile failed for '{uri}': "
            + ",".join(result.get("errors") or [])
        )
