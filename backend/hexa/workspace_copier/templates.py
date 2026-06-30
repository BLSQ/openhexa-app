"""Pipeline template copy: server-wide templates copied to a target server.

Templates are globally visible, so this runs once per target server,
independently of any workspace copy (it is *not* a per-workspace
:class:`~hexa.workspace_copier.resources.base.ResourceCopier` in the
orchestrator registry). Each source template is recreated on the target by:

1. Locating a host pipeline that can back the template on target:
   - Prefer the *already-copied* source pipeline (in its original workspace on
     target) if it exists — keeps the underlying pipeline visible inside its
     real workspace.
   - Otherwise create a host pipeline inside a dedicated "Template pipelines"
     workspace.
2. Ensuring each template version's underlying pipeline version exists on the
   host pipeline (upload the source zipfile if missing).
3. Calling ``createPipelineTemplateVersion`` per missing template version, in
   source ``versionNumber`` order. The first call also creates the
   ``PipelineTemplate`` on target (via ``Pipeline.get_or_create_template``).
4. Applying metadata (description / functionalType / tags) via
   ``updatePipelineTemplate``.

Idempotent: matches templates by name (globally unique) and existing versions
by ``versionNumber``.

Reuses :func:`~hexa.workspace_copier.resources.pipelines._upload_version` to
back template versions, and emits all progress through a
:class:`~hexa.workspace_copier.progress.ProgressReporter` rather than printing.
"""

import time
from typing import Any

from openhexa.graphql.graphql_client.client import Client
from openhexa.graphql.graphql_client.input_types import (
    CreatePipelineInput,
    CreateWorkspaceInput,
)

from hexa.workspace_copier.progress import ProgressReporter
from hexa.workspace_copier.resources.pipelines import _upload_version
from hexa.workspace_copier.results import TemplatesResult
from hexa.workspace_copier.transport import GraphQLError, gql

TEMPLATES_PAGE_SIZE = 50
TEMPLATE_VERSIONS_PAGE_SIZE = 50
PIPELINE_VERSIONS_PAGE_SIZE = 100

HOST_WORKSPACE_NAME = "Template pipelines"

# Templates are almost always copied *from* production, so both entry points
# default the source to it.
DEFAULT_SOURCE_URL = "https://api.openhexa.org/graphql/"

# Back-off between createPipelineTemplateVersion calls. Each one triggers
# auto-update of every dependent pipeline server-side, which can be heavy.
PER_VERSION_DELAY_SECONDS = 0.5


LIST_SOURCE_TEMPLATES_QUERY = """
query ListSourceTemplates($page: Int!, $perPage: Int!) {
    pipelineTemplates(page: $page, perPage: $perPage) {
        pageNumber totalPages totalItems
        items {
            id name code description functionalType
            validatedAt
            tags { name }
            sourcePipeline { id code name workspace { slug } }
        }
    }
}
"""

LIST_TARGET_TEMPLATES_QUERY = """
query ListTargetTemplates($page: Int!, $perPage: Int!) {
    pipelineTemplates(page: $page, perPage: $perPage) {
        pageNumber totalPages
        items {
            id name code
            sourcePipeline { id code workspace { slug } }
        }
    }
}
"""

TEMPLATE_VERSIONS_QUERY = """
query TemplateVersions($code: String!, $page: Int!, $perPage: Int!) {
    templateByCode(code: $code) {
        id name
        versions(page: $page, perPage: $perPage) {
            pageNumber totalPages
            items {
                id versionNumber changelog
                sourcePipelineVersion {
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
}
"""

TARGET_TEMPLATE_VERSIONS_QUERY = """
query TargetTemplateVersions($code: String!, $page: Int!, $perPage: Int!) {
    templateByCode(code: $code) {
        id
        versions(page: $page, perPage: $perPage) {
            pageNumber totalPages
            items { id versionNumber }
        }
    }
}
"""

HOST_PIPELINE_VERSIONS_QUERY = """
query HostPipelineVersions($id: UUID!, $page: Int!, $perPage: Int!) {
    pipeline(id: $id) {
        id
        versions(page: $page, perPage: $perPage) {
            pageNumber totalPages
            items { id versionNumber }
        }
    }
}
"""

CREATE_TEMPLATE_VERSION_MUTATION = """
mutation CreateTemplateVersion($input: CreatePipelineTemplateVersionInput!) {
    createPipelineTemplateVersion(input: $input) {
        success errors
        pipelineTemplate { id name code }
    }
}
"""

UPDATE_TEMPLATE_MUTATION = """
mutation UpdateTemplate($input: UpdateTemplateInput!) {
    updatePipelineTemplate(input: $input) {
        success errors
        template { id }
    }
}
"""


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def copy_templates(
    source: Client,
    target: Client,
    *,
    target_organization_id: str,
    reporter: ProgressReporter,
) -> TemplatesResult:
    """Copy every pipeline template from ``source`` into ``target``.

    ``target_organization_id`` is the organization the dedicated "Template
    pipelines" host workspace is created under when it doesn't already exist on
    the target.
    """
    result = TemplatesResult()

    reporter.info(f"=> Ensuring '{HOST_WORKSPACE_NAME}' workspace exists on target ...")
    host_ws_slug = _ensure_host_workspace(target, target_organization_id)
    reporter.info(f"   host workspace slug: '{host_ws_slug}'")

    # Listed once so re-runs find host pipelines whose code the server
    # re-derived from name (e.g. underscores -> dashes), not the source's
    # raw code.
    host_pipelines_by_name = _list_pipelines_by_name(target, host_ws_slug)

    reporter.info("=> Listing source templates ...")
    src_templates = _list_all_source_templates(source)
    reporter.info(f"   found {len(src_templates)} template(s)")

    reporter.info("=> Listing existing target templates ...")
    target_by_name = _list_all_target_templates(target)
    reporter.info(f"   target already has {len(target_by_name)} template(s)")

    for src in src_templates:
        try:
            _migrate_one(
                source,
                target,
                src,
                target_by_name,
                host_ws_slug,
                host_pipelines_by_name,
                result,
                reporter,
            )
        except GraphQLError as exc:
            msg = f"template '{src['name']}' (code='{src['code']}'): {exc}"
            result.warnings.append(msg)
            reporter.error(f"     FAILED: {msg}")

    return result


def _migrate_one(
    source: Client,
    target: Client,
    src_template: dict[str, Any],
    target_by_name: dict[str, dict[str, Any]],
    host_ws_slug: str,
    host_pipelines_by_name: dict[str, str],
    result: TemplatesResult,
    reporter: ProgressReporter,
) -> None:
    name = src_template["name"]
    code = src_template["code"]
    reporter.info(f"   - template '{name}' (code='{code}') ...")

    src_pipe = src_template.get("sourcePipeline")
    if src_pipe is None:
        result.warnings.append(
            f"template '{name}' has no source pipeline on source — skipped."
        )
        return

    existing_target = target_by_name.get(name)

    # 1. Decide host (workspace_slug, pipeline_code) and existing version numbers.
    if existing_target is not None:
        host_pipe_code = existing_target["sourcePipeline"]["code"]
        host_pipe_ws = existing_target["sourcePipeline"]["workspace"]["slug"]
        existing_version_numbers = _fetch_target_template_version_numbers(target, code)
        reporter.info(
            f"       already exists on target at "
            f"'{host_pipe_ws}/{host_pipe_code}'; "
            f"{len(existing_version_numbers)} version(s) present"
        )
    else:
        host_pipe_code, host_pipe_ws = _resolve_or_create_host_pipeline(
            target, src_pipe, host_ws_slug, host_pipelines_by_name, reporter
        )
        existing_version_numbers = set()

    # 2. Resolve host pipeline id and the versions it already has (by number).
    host_pipe = target.pipeline(
        workspace_slug=host_pipe_ws, pipeline_code=host_pipe_code
    )
    if host_pipe is None:
        raise GraphQLError(
            f"host pipeline '{host_pipe_ws}/{host_pipe_code}' could not be looked up"
        )
    host_pipe_id = str(host_pipe.id)
    host_versions_by_number = _fetch_pipeline_versions_by_number(target, host_pipe_id)

    # 3. Add missing template versions.
    src_versions = _fetch_source_template_versions(source, code)
    if not src_versions:
        result.warnings.append(
            f"template '{name}' has no versions on source — skipped."
        )
        return

    added: list[int] = []
    target_template_id: str | None = (
        existing_target["id"] if existing_target is not None else None
    )

    for ver in src_versions:
        vnum = ver["versionNumber"]
        if vnum in existing_version_numbers:
            continue

        src_pipe_ver = ver["sourcePipelineVersion"]
        target_pv_id = _ensure_host_pipeline_version(
            target,
            host_pipe_ws,
            host_pipe_code,
            src_pipe_ver,
            host_versions_by_number,
            reporter,
        )

        input_: dict[str, Any] = {
            "workspaceSlug": host_pipe_ws,
            "pipelineId": host_pipe_id,
            "pipelineVersionId": target_pv_id,
            "name": name,
            "code": code,
            "description": src_template.get("description") or "",
            "changelog": ver.get("changelog") or None,
            # versionName / documentation are not queryable on older source
            # servers, so let the target extract documentation from the
            # zipfile's README on its own (server default behavior).
        }
        input_ = {k: v for k, v in input_.items() if v is not None}

        data = gql(
            target,
            CREATE_TEMPLATE_VERSION_MUTATION,
            {"input": input_},
            "CreateTemplateVersion",
        )
        cptv = data["createPipelineTemplateVersion"]
        if not cptv["success"]:
            raise GraphQLError(
                f"createPipelineTemplateVersion v{vnum} failed: "
                + ",".join(cptv.get("errors") or [])
            )
        if target_template_id is None and cptv.get("pipelineTemplate"):
            target_template_id = cptv["pipelineTemplate"]["id"]

        reporter.info(f"       added template version v{vnum}")
        added.append(vnum)
        time.sleep(PER_VERSION_DELAY_SECONDS)

    if added:
        if existing_target is None:
            result.created.append(name)
        result.versions_added.append((name, added))
    else:
        result.skipped_unchanged.append(name)

    # 4. Apply metadata (idempotent re-application is fine).
    if target_template_id is not None:
        _apply_metadata(target, src_template, target_template_id, reporter)

    # 5. Warn on validated-on-source.
    if src_template.get("validatedAt"):
        result.warnings.append(
            f"template '{name}' is an official Bluesquare template on source; "
            "on target it will appear as a community template "
            "(validatedAt is not settable via the API)."
        )


# ---------------------------------------------------------------------------
# Host workspace & host pipeline
# ---------------------------------------------------------------------------


def _ensure_host_workspace(target: Client, organization_id: str) -> str:
    """Return the slug of the target workspace named HOST_WORKSPACE_NAME, creating it if needed."""
    page = 1
    while True:
        page_result = target.workspaces(page=page, per_page=100)
        for ws in page_result.items:
            if ws.name == HOST_WORKSPACE_NAME:
                return ws.slug
        if page >= page_result.total_pages or page_result.total_pages == 0:
            break
        page += 1

    created = target.create_workspace(
        input=CreateWorkspaceInput(
            name=HOST_WORKSPACE_NAME,
            description=(
                "Host workspace for source pipelines backing copied templates. "
                "Auto-created by the template copier."
            ),
            countries=[],
            load_sample_data=False,
            configuration={},
            organization_id=organization_id,
        )
    )
    if not created.success or created.workspace is None:
        raise GraphQLError(
            f"could not create '{HOST_WORKSPACE_NAME}' workspace: "
            + ",".join(created.errors or [])
        )
    return created.workspace.slug


def _resolve_or_create_host_pipeline(
    target: Client,
    src_pipeline: dict[str, Any],
    host_ws_slug: str,
    host_pipelines_by_name: dict[str, str],
    reporter: ProgressReporter,
) -> tuple[str, str]:
    """Return (pipeline_code, workspace_slug) of the host pipeline to use.

    Reuses the source pipeline in its original workspace on target if it exists
    there (because the workspace copy already brought it over). Otherwise reuses
    or creates a host pipeline in HOST_WORKSPACE_NAME, matched by source pipeline
    name (since the server re-derives code from name on create, e.g. dropping
    underscores).
    """
    src_code = src_pipeline["code"]
    src_name = src_pipeline["name"] or src_code
    src_ws = src_pipeline.get("workspace") or {}
    src_ws_slug = src_ws.get("slug")

    if src_ws_slug:
        existing = target.pipeline(workspace_slug=src_ws_slug, pipeline_code=src_code)
        if existing is not None:
            reporter.info(
                f"       reusing already-copied source pipeline "
                f"'{src_ws_slug}/{existing.code}'"
            )
            return existing.code, src_ws_slug

    # Fallback: ensure pipeline exists inside the dedicated host workspace.
    if src_name in host_pipelines_by_name:
        host_code = host_pipelines_by_name[src_name]
        reporter.info(
            f"       reusing existing host pipeline '{host_ws_slug}/{host_code}'"
        )
        return host_code, host_ws_slug

    create_result = target.create_pipeline(
        input=CreatePipelineInput(
            name=src_name,
            workspace_slug=host_ws_slug,
        )
    )
    if not create_result.success or create_result.pipeline is None:
        raise GraphQLError(
            f"createPipeline for template host '{src_code}' failed: "
            + ",".join(e.value for e in (create_result.errors or []))
        )
    new_code = create_result.pipeline.code
    host_pipelines_by_name[src_name] = new_code
    reporter.info(f"       created host pipeline '{host_ws_slug}/{new_code}'")
    return new_code, host_ws_slug


def _ensure_host_pipeline_version(
    target: Client,
    ws_slug: str,
    pipeline_code: str,
    src_pipeline_version: dict[str, Any],
    host_versions_by_number: dict[int, str],
    reporter: ProgressReporter,
) -> str:
    """Return the target pipelineVersion id for the given source pipeline version.

    Reuses an existing version on the host pipeline if one with the same
    versionNumber exists; otherwise uploads the source zipfile and records the
    new id in ``host_versions_by_number``.
    """
    src_vnum = src_pipeline_version["versionNumber"]
    if src_vnum in host_versions_by_number:
        return host_versions_by_number[src_vnum]

    if not src_pipeline_version.get("zipfile"):
        raise GraphQLError(
            f"source pipeline version v{src_vnum} has no zipfile; cannot upload"
        )

    up = _upload_version(target, ws_slug, pipeline_code, src_pipeline_version)
    reporter.info(
        f"       uploaded host pipeline version v{src_vnum} -> {up['versionName']}"
    )
    host_versions_by_number[up["versionNumber"]] = up["id"]
    return up["id"]


# ---------------------------------------------------------------------------
# Source / target fetch helpers
# ---------------------------------------------------------------------------


def _list_pipelines_by_name(target: Client, ws_slug: str) -> dict[str, str]:
    """List pipelines in ``ws_slug``, return {pipeline.name: pipeline.code}."""
    by_name: dict[str, str] = {}
    page = 1
    while True:
        result = target.pipelines(workspace_slug=ws_slug, page=page, per_page=100)
        for item in result.items:
            if item.name:
                by_name[item.name] = item.code
        if page >= result.total_pages or result.total_pages == 0:
            break
        page += 1
    return by_name


def _list_all_source_templates(source: Client) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    page = 1
    while True:
        data = gql(
            source,
            LIST_SOURCE_TEMPLATES_QUERY,
            {"page": page, "perPage": TEMPLATES_PAGE_SIZE},
            "ListSourceTemplates",
        )
        page_data = data["pipelineTemplates"]
        items.extend(page_data["items"])
        if page >= page_data["totalPages"] or page_data["totalPages"] == 0:
            break
        page += 1
    return items


def _list_all_target_templates(target: Client) -> dict[str, dict[str, Any]]:
    """Return target templates keyed by name (globally unique)."""
    by_name: dict[str, dict[str, Any]] = {}
    page = 1
    while True:
        data = gql(
            target,
            LIST_TARGET_TEMPLATES_QUERY,
            {"page": page, "perPage": TEMPLATES_PAGE_SIZE},
            "ListTargetTemplates",
        )
        page_data = data["pipelineTemplates"]
        for item in page_data["items"]:
            by_name[item["name"]] = item
        if page >= page_data["totalPages"] or page_data["totalPages"] == 0:
            break
        page += 1
    return by_name


def _fetch_source_template_versions(source: Client, code: str) -> list[dict[str, Any]]:
    versions: list[dict[str, Any]] = []
    page = 1
    while True:
        data = gql(
            source,
            TEMPLATE_VERSIONS_QUERY,
            {"code": code, "page": page, "perPage": TEMPLATE_VERSIONS_PAGE_SIZE},
            "TemplateVersions",
        )
        t = data["templateByCode"]
        if t is None:
            return []
        pg = t["versions"]
        versions.extend(pg["items"])
        if page >= pg["totalPages"] or pg["totalPages"] == 0:
            break
        page += 1
    return sorted(versions, key=lambda v: v["versionNumber"])


def _fetch_target_template_version_numbers(target: Client, code: str) -> set[int]:
    out: set[int] = set()
    page = 1
    while True:
        data = gql(
            target,
            TARGET_TEMPLATE_VERSIONS_QUERY,
            {"code": code, "page": page, "perPage": TEMPLATE_VERSIONS_PAGE_SIZE},
            "TargetTemplateVersions",
        )
        t = data["templateByCode"]
        if t is None:
            return out
        pg = t["versions"]
        for v in pg["items"]:
            out.add(v["versionNumber"])
        if page >= pg["totalPages"] or pg["totalPages"] == 0:
            break
        page += 1
    return out


def _fetch_pipeline_versions_by_number(
    target: Client, pipeline_id: str
) -> dict[int, str]:
    out: dict[int, str] = {}
    page = 1
    while True:
        data = gql(
            target,
            HOST_PIPELINE_VERSIONS_QUERY,
            {"id": pipeline_id, "page": page, "perPage": PIPELINE_VERSIONS_PAGE_SIZE},
            "HostPipelineVersions",
        )
        p = data["pipeline"]
        if p is None:
            return out
        pg = p["versions"]
        for v in pg["items"]:
            out[v["versionNumber"]] = v["id"]
        if page >= pg["totalPages"] or pg["totalPages"] == 0:
            break
        page += 1
    return out


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


def _apply_metadata(
    target: Client,
    src_template: dict[str, Any],
    target_template_id: str,
    reporter: ProgressReporter,
) -> None:
    tags = [t["name"] for t in (src_template.get("tags") or [])]
    input_: dict[str, Any] = {
        "id": target_template_id,
        "description": src_template.get("description") or None,
        "functionalType": src_template.get("functionalType") or None,
        "tags": tags or None,
    }
    input_ = {k: v for k, v in input_.items() if v is not None}
    if list(input_.keys()) == ["id"]:
        return

    data = gql(
        target,
        UPDATE_TEMPLATE_MUTATION,
        {"input": input_},
        "UpdateTemplate",
    )
    upd = data["updatePipelineTemplate"]
    if not upd["success"]:
        reporter.warning(
            f"       updatePipelineTemplate failed for "
            f"'{src_template['name']}': " + ",".join(upd.get("errors") or [])
        )
