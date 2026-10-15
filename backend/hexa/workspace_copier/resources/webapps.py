"""Web app copier: copy every web app of the workspace.

A *static* web app is a row plus a git repository on the server's Forgejo, and
its published version is any commit of that repository, not necessarily the
latest. It is only copied when both workspaces are on this server — local
endpoints (CLI with blank URLs), or remote ones pointing at this server's own
GraphQL endpoint (the admin's blank URLs). Forgejo then clones the repository
into the target organization itself, which keeps every commit, branch, author
and date, has no file size limit, and keeps the commit shas, so the published
version carries over as-is; the row is written with the ORM. Across servers the
git history could only be replayed through the API, which loses authors and
dates and cannot carry large files, so static web apps are skipped there.

Iframe web apps carry no history and are recreated from their URL. Superset web
apps are skipped with a warning.

The remote side goes through raw ``gql()``: the pinned SDK has no web app
operations.
"""

from typing import Any

import httpx
import requests
from django.conf import settings
from openhexa.graphql.graphql_client.client import Client

from hexa.git.forgejo import ForgejoAPIError
from hexa.webapps.models import (
    GitWebapp,
    Webapp,
    create_webapp_slug,
    create_webapp_subdomain,
)
from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import ProgressReporter
from hexa.workspace_copier.resources.base import ResourceCopier
from hexa.workspace_copier.results import CopyResult, WebappsResult
from hexa.workspace_copier.transport import GraphQLError, gql
from hexa.workspaces.models import Workspace

WEBAPPS_PAGE_SIZE = 50

NOT_COPIED_NOTE = (
    "web app subdomains, custom domains, favorites and the 'powered by' setting "
    "are not copied: the target assigns new subdomains, so public web app URLs "
    "change."
)

STATIC_ACROSS_SERVERS_WARNING = (
    "static web app '{slug}' was not copied: static web apps are only copied "
    "between workspaces of the same server (leave both server URLs blank)."
)

MIXED_ENDPOINTS_WARNING = (
    "web apps were not copied: they are copied when both workspaces are on the "
    "same server, or (iframe web apps only) when both are remote."
)

MIGRATION_REFUSED_HINT = (
    "Forgejo refused to clone from itself: add the host of GIT_SERVER_URL to "
    "its [migrations] ALLOWED_DOMAINS setting"
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
            }
        }
    }
}
"""

CREATE_WEBAPP_MUTATION = """
mutation CreateWebapp($input: CreateWebappInput!) {
    createWebapp(input: $input) {
        success errors
        webapp { slug }
    }
}
"""


class WebappsCopier(ResourceCopier):
    name = "webapps"
    label = "Web apps"
    help_text = (
        "Static web apps are copied with their full history when both workspaces "
        "are on this server (blank URLs). Superset web apps are skipped."
    )
    supports_local = True

    def copy(
        self,
        source: Endpoint,
        target: Endpoint,
        result: CopyResult,
        reporter: ProgressReporter,
        *,
        options: CopyOptions = CopyOptions(),
    ) -> None:
        result.webapps = WebappsResult()
        if source.is_local and target.is_local:
            self._copy_local(source, target, result.webapps, reporter)
        elif source.is_remote and target.is_remote:
            self._copy_remote(source, target, result.webapps, reporter)
        else:
            result.webapps.warnings.append(MIXED_ENDPOINTS_WARNING)
            reporter.warning(f"   {MIXED_ENDPOINTS_WARNING}")
            return
        if result.webapps.created:
            result.webapps.warnings.append(NOT_COPIED_NOTE)

    def _copy_local(
        self,
        source: Endpoint,
        target: Endpoint,
        wa_result: WebappsResult,
        reporter: ProgressReporter,
    ) -> None:
        target_ws = target.get_workspace("target")
        existing_names = set(
            Webapp.objects.filter(workspace=target_ws).values_list("name", flat=True)
        )
        webapps = Webapp.objects.filter(
            workspace=source.get_workspace("source")
        ).order_by("created_at")

        for webapp in webapps:
            if webapp.name in existing_names:
                wa_result.skipped.append(webapp.slug)
                reporter.info(f"   skipped web app '{webapp.slug}' (already exists)")
                continue
            if webapp.type == Webapp.WebappType.SUPERSET:
                wa_result.skipped.append(webapp.slug)
                wa_result.warnings.append(
                    f"Superset web app '{webapp.slug}' was not copied: recreate it "
                    "manually on the target."
                )
                reporter.warning(f"   skipped Superset web app '{webapp.slug}'")
                continue

            reporter.info(f"   copying web app '{webapp.slug}' ...")
            try:
                if webapp.type == Webapp.WebappType.STATIC:
                    copy = _copy_static_local(webapp.gitwebapp, target_ws)
                else:
                    copy = _new_webapp_row(Webapp, webapp, target_ws)
                    copy.save()
            except (ForgejoAPIError, requests.RequestException) as exc:
                wa_result.failed.append(webapp.slug)
                wa_result.warnings.append(
                    f"web app '{webapp.slug}' could not be copied — handle "
                    f"manually ({_describe_git_error(exc)})."
                )
                reporter.warning(f"   FAILED to copy web app '{webapp.slug}' ({exc})")
                continue
            wa_result.created.append(copy.slug)
            reporter.info(f"   created web app '{copy.slug}'")

    def _copy_remote(
        self,
        source: Endpoint,
        target: Endpoint,
        wa_result: WebappsResult,
        reporter: ProgressReporter,
    ) -> None:
        same_server = _on_this_server(source) and _on_this_server(target)
        if same_server:
            # Same database: the static copy below works on the rows directly.
            source_ws = Workspace.objects.get(slug=source.slug)
            target_ws = Workspace.objects.get(slug=target.slug)
        webapps = _list_webapps(source.client, source.slug)
        # Names are unique per workspace while target slugs may get a random
        # suffix, so the name is what identifies an already-copied web app.
        existing_names = {w["name"] for w in _list_webapps(target.client, target.slug)}

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
            if webapp["type"] == "STATIC" and not same_server:
                wa_result.skipped.append(src_slug)
                wa_result.warnings.append(
                    STATIC_ACROSS_SERVERS_WARNING.format(slug=src_slug)
                )
                reporter.warning(f"   skipped static web app '{src_slug}'")
                continue

            reporter.info(f"   copying web app '{src_slug}' ...")
            try:
                if webapp["type"] == "STATIC":
                    target_slug = _copy_static_local(
                        GitWebapp.objects.get(workspace=source_ws, slug=src_slug),
                        target_ws,
                    ).slug
                else:
                    target_slug = _create_on_target(
                        target.client,
                        target.slug,
                        webapp,
                        {"iframe": {"url": webapp["source"]["url"]}},
                    )
            except (ForgejoAPIError, requests.RequestException) as exc:
                wa_result.failed.append(src_slug)
                wa_result.warnings.append(
                    f"web app '{src_slug}' could not be copied — handle "
                    f"manually ({_describe_git_error(exc)})."
                )
                reporter.warning(f"   FAILED to copy web app '{src_slug}' ({exc})")
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
            wa_result.created.append(target_slug)
            reporter.info(f"   created web app '{target_slug}'")


# ---------------------------------------------------------------------------
# Same server
# ---------------------------------------------------------------------------


def _on_this_server(endpoint: Endpoint) -> bool:
    """Whether the endpoint is this server, reached locally or over GraphQL.

    The admin turns a blank server URL into this server's own GraphQL endpoint
    (built from ``INTERNAL_BASE_URL``, as the copy worker reaches the backend
    that way), so a remote endpoint at that URL is this server too.
    """
    if endpoint.is_local:
        return True
    this_server = f"{settings.INTERNAL_BASE_URL.rstrip('/')}/graphql"
    return str(endpoint.client.url).rstrip("/") == this_server


def _new_webapp_row(model: type[Webapp], webapp: Webapp, target_ws: Workspace):
    """Build an unsaved copy of ``webapp`` in ``target_ws``.

    The ORM is used directly rather than ``create_if_has_perm``: the copier is
    only reachable by superusers (admin) and operators (CLI), and on the same
    server the original author still exists, so the copy keeps it.
    """
    slug = create_webapp_slug(webapp.name, target_ws)
    return model(
        workspace=target_ws,
        type=webapp.type,
        name=webapp.name,
        slug=slug,
        subdomain=create_webapp_subdomain(slug, target_ws),
        description=webapp.description,
        icon=webapp.icon,
        url=webapp.url,
        is_public=webapp.is_public,
        allowed_operations=webapp.allowed_operations,
        created_by=webapp.created_by,
    )


def _copy_static_local(webapp: GitWebapp, target_ws: Workspace) -> GitWebapp:
    """Copy a static web app's row and repository, keeping its published version.

    The repository is created first: a failed clone leaves nothing behind
    (Forgejo deletes it), while a row without its repository would be broken.
    If the row then cannot be saved, the repository is deleted: re-runs skip
    web apps by name, but the leftover repository would block the next copy.
    """
    copy = _new_webapp_row(GitWebapp, webapp, target_ws)
    copy.repository = f"{target_ws.slug}-webapp-{copy.slug}"
    copy.published_commit = webapp.published_commit
    copy.copy_repo_from(webapp)
    try:
        copy.save()
    except Exception:
        copy.delete_repo()
        raise
    return copy


def _describe_git_error(exc: Exception) -> str:
    if (
        isinstance(exc, ForgejoAPIError)
        and exc.url.endswith("/repos/migrate")
        and "disallowed hosts" in exc.detail
    ):
        return MIGRATION_REFUSED_HINT
    return str(exc)


# ---------------------------------------------------------------------------
# Across servers
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


def _superset_warning(webapp: dict[str, Any]) -> str:
    source = webapp["source"]
    instance = source.get("instance") or {}
    return (
        f"Superset web app '{webapp['slug']}' was not copied: Superset instances "
        "are configured per server. Recreate it manually on the target (instance "
        f"'{instance.get('name')}' at {instance.get('url')}, dashboard "
        f"{source.get('dashboardId')})."
    )


def _create_on_target(
    client: Client,
    target_slug: str,
    webapp: dict[str, Any],
    source_input: dict[str, Any],
) -> str:
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
    return result["webapp"]["slug"]
