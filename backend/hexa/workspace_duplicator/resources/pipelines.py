"""Pipeline copier: list source pipelines, copy each (with versions) to target.

REMOTE branch — ported from ``migrate_lib/pipelines.py``. The LOCAL (ORM) branch
is implemented in a later phase. ``_upload_version`` is kept module-level because
the template copier reuses it to back template versions.

Declares ``depends_on=("files",)`` advisory dependency: *notebook* pipelines need
their ``.ipynb`` present on the target before ``createPipeline`` succeeds, so the
files copier should run first (zip pipelines don't need it).
"""

import base64
from typing import Any

from openhexa.graphql.graphql_client.client import Client
from openhexa.graphql.graphql_client.input_types import CreatePipelineInput

from hexa.workspace_duplicator.endpoints import Endpoint
from hexa.workspace_duplicator.resources.base import ResourceCopier
from hexa.workspace_duplicator.results import DuplicationResult, PipelinesResult
from hexa.workspace_duplicator.transport import GraphQLError, gql

PIPELINES_PAGE_SIZE = 50
VERSIONS_PAGE_SIZE = 50


PIPELINE_DETAIL_QUERY = """
query PipelineDetail($id: UUID!, $vPage: Int!, $vPerPage: Int!) {
    pipeline(id: $id) {
        id code name description type functionalType notebookPath
        schedule config webhookEnabled
        tags { name }
        scheduledPipelineVersion { id versionNumber }
        versions(page: $vPage, perPage: $vPerPage) {
            pageNumber
            totalPages
            items {
                id versionNumber name description externalLink config timeout
                zipfile
                parameters {
                    code name type multiple required default help
                    widget connection choices
                }
            }
        }
    }
}
"""

UPLOAD_PIPELINE_MUTATION = """
mutation UploadPipeline($input: UploadPipelineInput!) {
    uploadPipeline(input: $input) {
        success errors details
        pipelineVersion { id versionNumber versionName }
    }
}
"""

UPDATE_PIPELINE_MUTATION = """
mutation UpdatePipeline($input: UpdatePipelineInput!) {
    updatePipeline(input: $input) {
        success errors
        pipeline { id code }
    }
}
"""


class PipelinesCopier(ResourceCopier):
    name = "pipelines"
    label = "Pipelines (+versions)"
    depends_on = ("files",)

    def copy(
        self, source: Endpoint, target: Endpoint, result: DuplicationResult
    ) -> None:
        if source.is_remote and target.is_remote:
            self._copy_remote(source, target, result)
        else:
            raise NotImplementedError(
                "LOCAL pipelines copy (native ORM clone) is implemented in a "
                "later phase"
            )

    def _copy_remote(
        self, source: Endpoint, target: Endpoint, result: DuplicationResult
    ) -> None:
        pipes_result = PipelinesResult()
        result.pipelines = pipes_result

        pairs = _list_source_ids(source.client, source.slug)

        for pipeline_id, src_code in pairs:
            existing = target.client.pipeline(
                workspace_slug=target.slug, pipeline_code=src_code
            )
            if existing is not None:
                pipes_result.skipped.append(src_code)
                continue

            detail = _fetch_source_detail(source.client, pipeline_id)
            is_notebook = detail.get("type") == "notebook"

            if is_notebook and not detail.get("notebookPath"):
                pipes_result.warnings.append(
                    f"notebook pipeline '{src_code}' has no notebookPath; skipped."
                )
                pipes_result.skipped.append(src_code)
                continue

            target_pid, target_code = _create_on_target(
                target.client, target.slug, detail
            )
            if target_code != src_code:
                pipes_result.warnings.append(
                    f"pipeline created as '{target_code}' (source was '{src_code}'; "
                    "server re-derives the code from the name)."
                )

            uploaded_names, scheduled_version_id = _upload_versions(
                target.client,
                target.slug,
                target_code,
                detail,
                is_notebook,
                pipes_result,
            )

            _update_settings(target.client, target_pid, detail, scheduled_version_id)
            pipes_result.created.append((target_code, uploaded_names))


# ---------------------------------------------------------------------------
# Source fetch
# ---------------------------------------------------------------------------


def _list_source_ids(source: Client, slug: str) -> list[tuple[str, str]]:
    """Return [(pipeline_id, pipeline_code), ...] across all pages."""
    pairs: list[tuple[str, str]] = []
    page = 1
    while True:
        result = source.pipelines(
            workspace_slug=slug, page=page, per_page=PIPELINES_PAGE_SIZE
        )
        pairs.extend((str(item.id), item.code) for item in result.items)
        if page >= result.total_pages or result.total_pages == 0:
            break
        page += 1
    return pairs


def _fetch_source_detail(source: Client, pipeline_id: str) -> dict[str, Any]:
    """Fetch full pipeline data + all versions for one pipeline."""
    first = gql(
        source,
        PIPELINE_DETAIL_QUERY,
        {"id": pipeline_id, "vPage": 1, "vPerPage": VERSIONS_PAGE_SIZE},
        "PipelineDetail",
    )
    detail = first["pipeline"]
    if detail is None:
        raise GraphQLError(f"source pipeline id={pipeline_id} disappeared")
    versions = list(detail["versions"]["items"])
    total_pages = detail["versions"]["totalPages"]
    for vpage in range(2, total_pages + 1):
        more = gql(
            source,
            PIPELINE_DETAIL_QUERY,
            {"id": pipeline_id, "vPage": vpage, "vPerPage": VERSIONS_PAGE_SIZE},
            "PipelineDetail",
        )
        versions.extend(more["pipeline"]["versions"]["items"])
    detail["versions"] = sorted(versions, key=lambda v: v["versionNumber"])
    return detail


# ---------------------------------------------------------------------------
# Target writes
# ---------------------------------------------------------------------------


def _create_on_target(
    target: Client, target_slug: str, src_pipeline: dict[str, Any]
) -> tuple[str, str]:
    """Create an empty pipeline on the target and return (id, code).

    The server (see ``Pipeline.objects.create_if_has_perm`` in
    openhexa-app/.../pipelines/models.py) auto-generates the pipeline
    code from ``slugify(name)`` with a collision suffix and rejects any
    code the caller tries to pass. So we never pass a code; we always
    read the actual one back from the response.
    """
    is_notebook = src_pipeline.get("type") == "notebook"
    tags = [t["name"] for t in (src_pipeline.get("tags") or [])]
    create_input = CreatePipelineInput(
        name=src_pipeline["name"] or src_pipeline["code"],
        description=src_pipeline.get("description") or None,
        workspace_slug=target_slug,
        notebook_path=src_pipeline.get("notebookPath") if is_notebook else None,
        functional_type=src_pipeline.get("functionalType"),
        tags=tags or None,
    )
    result = target.create_pipeline(input=create_input)
    if not result.success or result.pipeline is None:
        raise GraphQLError(
            f"createPipeline failed for '{src_pipeline['code']}': "
            + ",".join(e.value for e in (result.errors or []))
        )
    created_code = result.pipeline.code

    # createPipeline returns only the code; fetch by code to get the id
    # needed for subsequent updatePipeline.
    created = target.pipeline(workspace_slug=target_slug, pipeline_code=created_code)
    if created is None:
        raise GraphQLError(f"could not look up created pipeline '{created_code}'")
    return str(created.id), created_code


def _clean_parameters(parameters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Strip nulls that the input type doesn't accept verbatim."""
    cleaned = []
    for p in parameters:
        item = {k: v for k, v in p.items() if v is not None}
        cfile = item.get("choicesFromFile")
        if cfile is not None:
            item["choicesFromFile"] = {k: v for k, v in cfile.items() if v is not None}
        cleaned.append(item)
    return cleaned


def _upload_version(
    target: Client,
    workspace_slug: str,
    pipeline_code: str,
    version: dict[str, Any],
) -> dict[str, Any]:
    """Upload one version to an existing target pipeline."""
    try:
        base64.b64decode(version["zipfile"], validate=True)
    except Exception as exc:
        raise GraphQLError(
            f"version {version['versionNumber']} has invalid base64 zipfile: {exc}"
        )

    input_: dict[str, Any] = {
        "workspaceSlug": workspace_slug,
        "pipelineCode": pipeline_code,
        "name": version.get("name"),
        "description": version.get("description"),
        "externalLink": version.get("externalLink"),
        "parameters": _clean_parameters(version.get("parameters") or []),
        "zipfile": version["zipfile"],
        "config": version.get("config") or {},
        "timeout": version.get("timeout"),
    }
    input_ = {k: v for k, v in input_.items() if v is not None}
    data = gql(target, UPLOAD_PIPELINE_MUTATION, {"input": input_}, "UploadPipeline")
    result = data["uploadPipeline"]
    if not result["success"]:
        raise GraphQLError(
            f"uploadPipeline failed for {pipeline_code} v{version['versionNumber']}: "
            + ",".join(result.get("errors") or [])
            + (f" ({result['details']})" if result.get("details") else "")
        )
    return result["pipelineVersion"]


def _update_settings(
    target: Client,
    target_pipeline_id: str,
    src_pipeline: dict[str, Any],
    scheduled_version_id: str | None,
) -> None:
    """Apply pipeline-level fields that createPipeline/uploadPipeline cannot set."""
    input_: dict[str, Any] = {
        "id": target_pipeline_id,
        "schedule": src_pipeline.get("schedule"),
        "webhookEnabled": src_pipeline.get("webhookEnabled"),
        "config": src_pipeline.get("config") or None,
        "scheduledPipelineVersionId": scheduled_version_id,
        "autoUpdateFromTemplate": False,
    }
    # Only call updatePipeline if at least one migrated field has a value.
    meaningful = {
        k: v
        for k, v in input_.items()
        if k != "id"
        and k != "autoUpdateFromTemplate"
        and v not in (None, False, {}, "")
    }
    if not meaningful:
        return
    input_ = {k: v for k, v in input_.items() if v is not None}
    data = gql(target, UPDATE_PIPELINE_MUTATION, {"input": input_}, "UpdatePipeline")
    result = data["updatePipeline"]
    if not result["success"]:
        raise GraphQLError(
            f"updatePipeline failed for {src_pipeline['code']}: "
            + ",".join(result.get("errors") or [])
        )


def _upload_versions(
    target: Client,
    target_slug: str,
    target_code: str,
    detail: dict[str, Any],
    is_notebook: bool,
    result: PipelinesResult,
) -> tuple[list[str], str | None]:
    """Upload all zipfile versions; return (uploaded_version_names, scheduled_version_id)."""
    uploaded_names: list[str] = []
    scheduled_version_id: str | None = None
    scheduled_src = detail.get("scheduledPipelineVersion") or {}
    scheduled_src_number = scheduled_src.get("versionNumber")

    if is_notebook:
        if detail.get("versions"):
            result.warnings.append(
                f"pipeline '{target_code}' has {len(detail['versions'])} version(s) "
                "on the source, but uploadPipeline is not supported for "
                "notebook pipelines — versions were not migrated."
            )
        return uploaded_names, scheduled_version_id

    versions = detail.get("versions") or []
    if not versions:
        result.warnings.append(
            f"pipeline '{target_code}' has no versions on source; created with no version."
        )
    for v in versions:
        up = _upload_version(target, target_slug, target_code, v)
        uploaded_names.append(up["versionName"])
        if (
            scheduled_src_number is not None
            and up.get("versionNumber") == scheduled_src_number
        ):
            scheduled_version_id = up["id"]
    return uploaded_names, scheduled_version_id
