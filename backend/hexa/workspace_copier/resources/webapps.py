"""Web app copier: copy every web app of the workspace, with its full history.

A *static* web app is a git repository whose versions are the commits of its
``main`` branch, and the published version (``GitSource.publishedVersion``) is
any one of them — not necessarily the latest, since a user can roll back. So
copying only the latest content would be wrong: the history is replayed commit
by commit, oldest first, and the target commit matching the source's published
one is published last. The target's git server assigns new shas, which is why
each source sha is mapped to the target sha its replay produced.

Iframe web apps carry no history and are recreated from their URL. Superset web
apps point at a Superset instance by its id on the source server, which means
nothing on the target, so they are skipped with a warning.

Everything goes through raw ``gql()``: the pinned SDK has no web app operations.
"""

from typing import Any

import httpx
from openhexa.graphql.graphql_client.client import Client

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import ProgressReporter
from hexa.workspace_copier.resources.base import ResourceCopier
from hexa.workspace_copier.results import CopyResult, WebappsResult
from hexa.workspace_copier.transport import GraphQLError, gql

WEBAPPS_PAGE_SIZE = 50
VERSIONS_PAGE_SIZE = 50

NOT_COPIED_NOTE = (
    "web app subdomains, custom domains, favorites, the 'powered by' setting and "
    "commit authors/dates are not copied: the target assigns new subdomains, so "
    "public web app URLs change."
)


LIST_WEBAPPS_QUERY = """
query ListWorkspaceWebapps($slug: String!, $page: Int!, $perPage: Int!) {
    webapps(workspaceSlug: $slug, page: $page, perPage: $perPage) {
        totalPages
        items {
            id slug name description type icon isPublic allowedOperations
            source {
                __typename
                ... on IframeSource { url }
                ... on SupersetSource { dashboardId instance { name url } }
                ... on GitSource { publishedVersion }
            }
        }
    }
}
"""

WEBAPP_VERSIONS_QUERY = """
query WebappVersions($workspaceSlug: String!, $slug: String!, $page: Int!, $perPage: Int!) {
    webapp(workspaceSlug: $workspaceSlug, slug: $slug) {
        versions(page: $page, perPage: $perPage) {
            items { id message }
        }
    }
}
"""

WEBAPP_FILES_QUERY = """
query WebappFiles($workspaceSlug: String!, $slug: String!, $ref: String!) {
    webapp(workspaceSlug: $workspaceSlug, slug: $slug) {
        files(ref: $ref) { path type content encoding tooLarge }
    }
}
"""

UPDATE_WEBAPP_INPUT_FIELDS_QUERY = """
query UpdateWebappInputFields {
    __type(name: "UpdateWebappInput") { inputFields { name } }
}
"""

CREATE_WEBAPP_MUTATION = """
mutation CreateWebapp($input: CreateWebappInput!) {
    createWebapp(input: $input) {
        success errors
        webapp { id slug source { ... on GitSource { publishedVersion } } }
    }
}
"""

UPDATE_WEBAPP_MUTATION = """
mutation UpdateWebapp($input: UpdateWebappInput!) {
    updateWebapp(input: $input) {
        success errors
        webapp { source { ... on GitSource { publishedVersion } } }
    }
}
"""

DELETE_WEBAPP_MUTATION = """
mutation DeleteWebapp($input: DeleteWebappInput!) {
    deleteWebapp(input: $input) { success errors }
}
"""


class IncompleteWebappCopy(Exception):
    """The web app was fully replayed on the target but needs a manual fix.

    Unlike a replay failure, the target web app is kept: its history is complete,
    only the step named in the message is missing.
    """


class WebappsCopier(ResourceCopier):
    name = "webapps"
    label = "Web apps (+versions)"
    help_text = (
        "Static web apps are copied with every version and keep the same published "
        "version. Superset web apps are skipped."
    )

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
            self._copy_remote(source, target, result, reporter)
        else:
            raise NotImplementedError(
                "LOCAL web apps copy (native ORM clone) is implemented in a later "
                "phase"
            )

    def _copy_remote(
        self,
        source: Endpoint,
        target: Endpoint,
        result: CopyResult,
        reporter: ProgressReporter,
    ) -> None:
        wa_result = WebappsResult()
        result.webapps = wa_result

        webapps = _list_webapps(source.client, source.slug)
        # Names are unique per workspace while target slugs may get a random
        # suffix, so the name is what identifies an already-copied web app.
        existing_names = {w["name"] for w in _list_webapps(target.client, target.slug)}
        keeps_messages = None

        for webapp in webapps:
            src_slug = webapp["slug"]
            if webapp["name"] in existing_names:
                wa_result.skipped.append(src_slug)
                reporter.info(f"   skipped web app '{src_slug}' (already exists)")
                continue
            if webapp["type"] == "SUPERSET":
                wa_result.skipped.append(src_slug)
                wa_result.warnings.append(_superset_warning(webapp))
                reporter.warning(f"   skipped Superset web app '{src_slug}'")
                continue

            reporter.info(f"   copying web app '{src_slug}' ...")
            try:
                if webapp["type"] == "STATIC":
                    if keeps_messages is None:
                        keeps_messages = _supports_commit_message(target.client)
                        if not keeps_messages:
                            wa_result.warnings.append(
                                "the target server does not accept commit messages "
                                "on web app updates: replayed versions are titled "
                                "'Update webapp content'."
                            )
                    target_slug, versions = _copy_static(
                        source, target, webapp, keeps_messages, wa_result, reporter
                    )
                else:
                    target_slug = _create_on_target(
                        target.client,
                        target.slug,
                        webapp,
                        {"iframe": {"url": webapp["source"]["url"]}},
                    )["slug"]
                    versions = 0
            except IncompleteWebappCopy as exc:
                wa_result.failed.append(src_slug)
                wa_result.warnings.append(
                    f"web app '{src_slug}' was copied but is incomplete — fix it "
                    f"manually on the target ({exc})."
                )
                reporter.warning(f"   INCOMPLETE web app '{src_slug}' ({exc})")
                continue
            except (GraphQLError, httpx.HTTPError) as exc:
                # Per-app like the other copiers, and httpx too: a timeout on one
                # web app must not abort the ones after it.
                wa_result.failed.append(src_slug)
                wa_result.warnings.append(
                    f"web app '{src_slug}' could not be copied — handle manually "
                    f"({exc})."
                )
                reporter.warning(f"   FAILED to copy web app '{src_slug}' ({exc})")
                continue
            wa_result.created.append((target_slug, versions))
            reporter.info(f"   created web app '{target_slug}' ({versions} version(s))")

        if wa_result.created:
            wa_result.warnings.append(NOT_COPIED_NOTE)


# ---------------------------------------------------------------------------
# Source fetch
# ---------------------------------------------------------------------------


def _list_webapps(client: Client, slug: str) -> list[dict[str, Any]]:
    webapps: list[dict[str, Any]] = []
    page = 1
    while True:
        data = gql(
            client,
            LIST_WEBAPPS_QUERY,
            {"slug": slug, "page": page, "perPage": WEBAPPS_PAGE_SIZE},
            "ListWorkspaceWebapps",
        )
        page_data = data["webapps"]
        webapps.extend(page_data["items"])
        if page >= page_data["totalPages"] or page_data["totalPages"] == 0:
            break
        page += 1
    return webapps


def _list_versions(client: Client, workspace_slug: str, slug: str) -> list[dict]:
    """Return every commit of the web app, oldest first.

    ``versions`` has no page count, so pages are read until a short one.
    """
    versions: list[dict[str, Any]] = []
    page = 1
    while True:
        data = gql(
            client,
            WEBAPP_VERSIONS_QUERY,
            {
                "workspaceSlug": workspace_slug,
                "slug": slug,
                "page": page,
                "perPage": VERSIONS_PAGE_SIZE,
            },
            "WebappVersions",
        )
        webapp = data["webapp"]
        if webapp is None:
            raise GraphQLError(f"source web app '{slug}' disappeared")
        items = (webapp["versions"] or {}).get("items") or []
        versions.extend(items)
        if len(items) < VERSIONS_PAGE_SIZE:
            break
        page += 1
    # The git server lists commits newest first; replay needs them oldest first.
    return versions[::-1]


def _fetch_tree(
    client: Client, workspace_slug: str, slug: str, ref: str
) -> dict[str, tuple[str, str]]:
    """Return ``{path: (content, encoding)}`` for every file at commit ``ref``.

    A file too large for the git API comes back without content; replaying the
    commit without it would silently produce a different web app, so it fails
    the web app instead.
    """
    data = gql(
        client,
        WEBAPP_FILES_QUERY,
        {"workspaceSlug": workspace_slug, "slug": slug, "ref": ref},
        "WebappFiles",
    )
    webapp = data["webapp"]
    if webapp is None:
        raise GraphQLError(f"source web app '{slug}' disappeared")
    tree = {}
    for node in webapp["files"] or []:
        if node["type"] != "file":
            continue
        if node.get("tooLarge") or node.get("content") is None:
            raise GraphQLError(
                f"file '{node['path']}' at version {ref[:8]} is too large to be "
                "copied through the API"
            )
        tree[node["path"]] = (node["content"], node["encoding"])
    return tree


def _superset_warning(webapp: dict[str, Any]) -> str:
    source = webapp["source"]
    instance = source.get("instance") or {}
    return (
        f"Superset web app '{webapp['slug']}' was not copied: Superset instances "
        "are configured per server. Recreate it manually on the target (instance "
        f"'{instance.get('name')}' at {instance.get('url')}, dashboard "
        f"{source.get('dashboardId')})."
    )


# ---------------------------------------------------------------------------
# Target writes
# ---------------------------------------------------------------------------


def _supports_commit_message(client: Client) -> bool:
    """Whether the target's ``updateWebapp`` accepts ``commitMessage``.

    Servers running a release older than that field reject the whole mutation
    when it is sent, so it is detected once rather than assumed.
    """
    data = gql(
        client,
        UPDATE_WEBAPP_INPUT_FIELDS_QUERY,
        operation_name="UpdateWebappInputFields",
    )
    fields = (data.get("__type") or {}).get("inputFields") or []
    return any(f["name"] == "commitMessage" for f in fields)


def _files_input(tree: dict[str, tuple[str, str]], paths) -> list[dict[str, str]]:
    return [
        {"path": path, "content": tree[path][0], "encoding": tree[path][1]}
        for path in sorted(paths)
    ]


def _create_on_target(
    client: Client,
    target_slug: str,
    webapp: dict[str, Any],
    source_input: dict[str, Any],
) -> dict[str, Any]:
    input_ = {
        "workspaceSlug": target_slug,
        "name": webapp["name"],
        "description": webapp.get("description") or "",
        "icon": webapp.get("icon"),
        "isPublic": webapp["isPublic"],
        "allowedOperations": webapp.get("allowedOperations") or [],
        "source": source_input,
    }
    data = gql(client, CREATE_WEBAPP_MUTATION, {"input": input_}, "CreateWebapp")
    result = data["createWebapp"]
    if not result["success"] or result.get("webapp") is None:
        raise GraphQLError(
            f"createWebapp failed for '{webapp['slug']}': "
            + ",".join(result.get("errors") or [])
        )
    return result["webapp"]


def _update_on_target(client: Client, input_: dict[str, Any]) -> str | None:
    """Run ``updateWebapp`` and return the web app's published sha afterwards."""
    data = gql(client, UPDATE_WEBAPP_MUTATION, {"input": input_}, "UpdateWebapp")
    result = data["updateWebapp"]
    if not result["success"] or result.get("webapp") is None:
        raise GraphQLError(
            "updateWebapp failed: " + ",".join(result.get("errors") or [])
        )
    return (result["webapp"]["source"] or {}).get("publishedVersion")


def _delete_on_target(client: Client, webapp_id: str) -> bool:
    try:
        data = gql(
            client,
            DELETE_WEBAPP_MUTATION,
            {"input": {"id": webapp_id}},
            "DeleteWebapp",
        )
    except (GraphQLError, httpx.HTTPError):
        return False
    return data["deleteWebapp"]["success"]


def _copy_static(
    source: Endpoint,
    target: Endpoint,
    webapp: dict[str, Any],
    keeps_messages: bool,
    wa_result: WebappsResult,
    reporter: ProgressReporter,
) -> tuple[str, int]:
    """Replay a static web app's history on the target; return (slug, versions).

    Each commit is sent as the difference from the previous one, so only what
    changed travels and only one tree is held in memory at a time. If the replay
    fails part-way, the half-built target web app is deleted: re-runs skip web
    apps by name, so leaving it would hide the failure forever.

    ``versions`` counts the commits actually created on the target.
    """
    src_slug = webapp["slug"]
    versions = _list_versions(source.client, source.slug, src_slug)
    if not versions:
        raise GraphQLError("the source web app has no version")

    first, *rest = versions
    tree = _fetch_tree(source.client, source.slug, src_slug, first["id"])
    created = _create_on_target(
        target.client, target.slug, webapp, {"static": _files_input(tree, tree)}
    )
    target_sha = created["source"]["publishedVersion"]
    sha_map = {first["id"]: target_sha}
    replayed = 1

    try:
        for version in rest:
            new_tree = _fetch_tree(source.client, source.slug, src_slug, version["id"])
            changed = [p for p in new_tree if tree.get(p) != new_tree[p]]
            deleted = [p for p in tree if p not in new_tree]
            if not changed and not deleted and new_tree:
                # Saving unchanged content is a real commit (the editor and agents
                # do it). Re-sending one unchanged file makes the git server create
                # one too; an empty file list would be a no-op.
                changed = [min(new_tree)]
            if changed or deleted:
                input_ = {
                    "id": created["id"],
                    "files": _files_input(new_tree, changed),
                    "filesToDelete": sorted(deleted),
                }
                if keeps_messages:
                    input_["commitMessage"] = version["message"]
                target_sha = _update_on_target(target.client, input_)
                replayed += 1
            sha_map[version["id"]] = target_sha
            tree = new_tree
        reporter.info(f"      replayed {replayed} version(s)")
    except (GraphQLError, httpx.HTTPError):
        if not _delete_on_target(target.client, created["id"]):
            wa_result.warnings.append(
                f"web app '{src_slug}' was partially created on the target and "
                "could not be deleted — delete it before re-running."
            )
        raise

    if replayed < len(versions):
        wa_result.warnings.append(
            f"web app '{src_slug}': {len(versions) - replayed} commit(s) with no "
            "files could not be recreated, so the target has fewer versions."
        )
    _publish(target.client, created["id"], webapp, versions, sha_map)
    return created["slug"], replayed


def _publish(
    client: Client,
    target_id: str,
    webapp: dict[str, Any],
    versions: list[dict[str, Any]],
    sha_map: dict[str, str],
) -> None:
    """Publish the target commit matching the source's published version.

    Every replayed commit publishes itself on the target, so the target ends up
    on its latest commit; this moves it back when the source had rolled back.
    Runs after the replay's delete-on-failure guard: the history is complete by
    now, so a failure here keeps the web app and only the publishing is left to
    do by hand.
    """
    published = webapp["source"].get("publishedVersion")
    if not published:
        return
    latest_target_sha = sha_map[versions[-1]["id"]]
    target_sha = sha_map.get(published)
    if target_sha is None:
        # A commit pushed outside main (the git proxy allows it) can be
        # published but is not in the replayed history.
        raise IncompleteWebappCopy(
            f"its published version {published[:8]} is not on its main history, "
            "so the latest version is published instead"
        )
    if target_sha != latest_target_sha:
        try:
            _update_on_target(
                client, {"id": target_id, "publishedVersionId": target_sha}
            )
        except (GraphQLError, httpx.HTTPError) as exc:
            raise IncompleteWebappCopy(
                f"publishing the version matching {published[:8]} failed ({exc})"
            ) from exc
