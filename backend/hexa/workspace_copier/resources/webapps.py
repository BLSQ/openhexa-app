"""Web app copier: copy every web app of the workspace.

A *static* web app is a row plus a git repository on the server's Forgejo, and
its published version is any commit of that repository, not necessarily the
latest. It is only copied in a same-server copy (``CopyOptions.same_server``),
when both workspaces are in this server's database. Forgejo then clones the repository
into the target organization itself, which keeps every commit, branch, author
and date, has no file size limit, and keeps the commit shas, so the published
version carries over as-is; the row is written with the ORM. Across servers the
git history could only be replayed through the API, which loses authors and
dates and cannot carry large files, so static web apps are skipped there.

Iframe web apps carry no history and are recreated from their URL over GraphQL.
A Superset web app points at a Superset instance that belongs to an organization,
so it is only copied in a same-server copy within the same organization, where
that instance is available to the target; otherwise it is skipped with a warning.

Web apps are listed and created through raw ``gql()``: the pinned SDK has no web
app operations.
"""

from typing import Any

import httpx
import requests
from openhexa.graphql.graphql_client.client import Client

from hexa.git.forgejo import ForgejoAPIError
from hexa.webapps.models import (
    GitWebapp,
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
    "when both workspaces are on this server (same-server copy)."
)

NOT_ON_THIS_SERVER_WARNING = (
    "static web app '{slug}' could not be copied: the workspaces are not both on "
    "this server, run the copy without the same-server option."
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
                ... on SupersetSource { dashboardId instance { id name url } }
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
        'Static web apps are copied with their full history only with "Both '
        'workspaces are on this server". Superset web apps only within the same '
        "organization on this server."
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
        wa_result = result.webapps = WebappsResult()
        source_ws = target_ws = None
        if options.same_server:
            # Same database: the static copy below works on the rows directly.
            source_ws = Workspace.objects.filter(slug=source.slug).first()
            target_ws = Workspace.objects.filter(slug=target.slug).first()
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
            if webapp["type"] == "SUPERSET" and not _same_organization(
                source_ws, target_ws
            ):
                wa_result.skipped.append(src_slug)
                wa_result.warnings.append(_superset_warning(webapp))
                reporter.warning(f"   skipped Superset web app '{src_slug}'")
                continue
            if webapp["type"] == "STATIC" and not options.same_server:
                wa_result.skipped.append(src_slug)
                wa_result.warnings.append(
                    STATIC_ACROSS_SERVERS_WARNING.format(slug=src_slug)
                )
                reporter.warning(f"   skipped static web app '{src_slug}'")
                continue
            if webapp["type"] == "STATIC" and (source_ws is None or target_ws is None):
                wa_result.failed.append(src_slug)
                wa_result.warnings.append(
                    NOT_ON_THIS_SERVER_WARNING.format(slug=src_slug)
                )
                reporter.warning(f"   FAILED to copy web app '{src_slug}'")
                continue

            reporter.info(f"   copying web app '{src_slug}' ...")
            try:
                if webapp["type"] == "STATIC":
                    target_slug = _copy_static(
                        GitWebapp.objects.get(workspace=source_ws, slug=src_slug),
                        target_ws,
                    ).slug
                else:
                    target_slug = _create_on_target(
                        target.client, target.slug, webapp, _source_input(webapp)
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
        if wa_result.created:
            wa_result.warnings.append(NOT_COPIED_NOTE)


# ---------------------------------------------------------------------------
# Same server
# ---------------------------------------------------------------------------


def _copy_static(webapp: GitWebapp, target_ws: Workspace) -> GitWebapp:
    """Copy a static web app's row and repository, keeping its published version.

    The row is written with the ORM rather than ``create_if_has_perm``: pre-flight
    already checked that the token can edit the target, and on the same server
    the original author still exists, so the copy keeps it.

    The repository is created first: a failed clone leaves nothing behind
    (Forgejo deletes it), while a row without its repository would be broken.
    If the row then cannot be saved, the repository is deleted: re-runs skip
    web apps by name, but the leftover repository would block the next copy.
    """
    slug = create_webapp_slug(webapp.name, target_ws)
    copy = GitWebapp(
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
        repository=f"{target_ws.slug}-webapp-{slug}",
        published_commit=webapp.published_commit,
    )
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
# GraphQL
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


def _same_organization(source_ws: Workspace | None, target_ws: Workspace | None):
    return (
        source_ws is not None
        and target_ws is not None
        and source_ws.organization_id == target_ws.organization_id
    )


def _source_input(webapp: dict[str, Any]) -> dict[str, Any]:
    source = webapp["source"]
    if webapp["type"] == "SUPERSET":
        return {
            "superset": {
                "instanceId": source["instance"]["id"],
                "dashboardId": source["dashboardId"],
            }
        }
    return {"iframe": {"url": source["url"]}}


def _superset_warning(webapp: dict[str, Any]) -> str:
    source = webapp["source"]
    instance = source.get("instance") or {}
    return (
        f"Superset web app '{webapp['slug']}' was not copied: Superset instances "
        "belong to an organization, so it is only copied when both workspaces are "
        "on this server and in the same organization. Recreate it manually on the "
        "target (instance "
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
