"""Shared entry point for the workspace copy flows (CLI + admin).

Builds source/target :class:`Endpoint`s from raw connection parameters and runs
the orchestrator. This is the single place both the management command and the
admin view call, so neither holds any orchestration logic — they stay dumb
wrappers around :func:`run_copy`.

Both sides are reached over GraphQL with a ServiceAccount Bearer token; a blank
server URL means this server's own GraphQL endpoint.

Every run starts with a verification step that builds both endpoints up front —
which authenticates against each server. Both sides are
checked even if the first fails, so the user sees every problem at once rather
than fixing them one round-trip at a time.
"""

from collections.abc import Callable
from typing import Any

import httpx
from django.conf import settings
from django.core.exceptions import ValidationError
from openhexa.graphql.graphql_client.client import Client

from hexa.user_management.models import Organization
from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.orchestrator import copy_workspace
from hexa.workspace_copier.progress import ProgressReporter
from hexa.workspace_copier.results import CopyResult, TemplatesResult
from hexa.workspace_copier.templates import copy_templates
from hexa.workspace_copier.transport import GraphQLError, build_client, gql
from hexa.workspaces.models import Workspace


def this_server_graphql_url() -> str:
    # The worker runs the copy, and INTERNAL_BASE_URL is how workers reach the
    # backend (pipelines and the dataset worker use it too).
    return f"{settings.INTERNAL_BASE_URL.rstrip('/')}/graphql/"


class CredentialError(GraphQLError):
    """One or both endpoints failed pre-flight verification.

    Carries one message per failing side so callers can show them together. It
    subclasses :class:`GraphQLError` so existing ``except GraphQLError`` handlers
    keep catching it.
    """

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def _build_source(url: str | None, token: str | None, slug: str) -> Endpoint:
    """Build the source endpoint, verifying the workspace exists.

    The lookup is what makes a wrong slug a pre-flight failure: the copiers read
    an absent source workspace as an *empty* one, so without it a typo would
    report a clean run that copied nothing. The workspace is stashed on the
    endpoint, so the copiers reuse it rather than fetching it again.
    """
    client = build_client(url or this_server_graphql_url(), token, label="source")
    workspace = client.workspace(slug=slug)
    if workspace is None:
        raise GraphQLError(f"source workspace '{slug}' not found")
    return Endpoint(client, slug, workspace=workspace)


def _build_target(
    url: str | None,
    token: str | None,
    organization_id: str | None,
    workspace_name: str | None,
    workspace_slug: str | None,
) -> Endpoint:
    if workspace_slug:
        return _build_existing_target(url, token, workspace_slug)
    client = build_client(url or this_server_graphql_url(), token, label="target")
    return Endpoint(
        client, organization_id=organization_id, workspace_name=workspace_name
    )


def _build_existing_target(
    url: str | None, token: str | None, workspace_slug: str
) -> Endpoint:
    """Build a target endpoint pointing at a pre-existing workspace.

    Used by the idempotent re-run flow (``--target-workspace-slug``): the target
    workspace is looked up instead of created, so a missing slug surfaces here as
    a verification failure — the run aborts before any copying rather than
    mid-way. With the slug already set on the endpoint, the workspace-metadata
    copier skips creation and the downstream copiers make the rest of the run
    idempotent by skipping resources that already exist.
    """
    client = build_client(url or this_server_graphql_url(), token, label="target")
    workspace = client.workspace(slug=workspace_slug)
    if workspace is None:
        raise GraphQLError(
            f"target workspace '{workspace_slug}' not found — create it first "
            "or omit --target-workspace-slug to create a new workspace."
        )
    return Endpoint(client, slug=workspace_slug, workspace=workspace)


WORKSPACE_ORGANIZATION_QUERY = """
query WorkspaceOrganization($slug: String!) {
  workspace(slug: $slug) {
    organization {
      id
    }
  }
}
"""

NOT_ON_THIS_SERVER_ERROR = (
    "{side}: workspace '{slug}' is not on this server, so it cannot be copied "
    "as a same-server copy."
)


def _is_on_this_server(endpoint: Endpoint) -> bool:
    # Slugs are only unique within one server, so a workspace with the same slug
    # here may not be the one the URL points at. Organization ids are UUIDs,
    # which no two servers share.
    data = gql(
        endpoint.client,
        WORKSPACE_ORGANIZATION_QUERY,
        {"slug": endpoint.slug},
        "WorkspaceOrganization",
    )
    organization_id = ((data.get("workspace") or {}).get("organization") or {}).get(
        "id"
    )
    return Workspace.objects.filter(
        slug=endpoint.slug, organization_id=organization_id
    ).exists()


def _organization_is_on_this_server(organization_id: str | None) -> bool:
    try:
        return Organization.objects.filter(id=organization_id).exists()
    except ValidationError:
        return False


def _same_server_errors(source: Endpoint, target: Endpoint) -> list[str]:
    """Check that a same-server copy really has both workspaces on this server.

    The flag is the operator's word that both sides are this server; if the
    URLs point elsewhere, the database and static web apps would be written to
    this server while everything else goes to the other one. A target still to
    be created is checked through the organization it will be created in.
    """
    errors = []
    sides = [("source", source)] + ([("target", target)] if target.slug else [])
    for side, endpoint in sides:
        try:
            on_this_server = _is_on_this_server(endpoint)
        except GraphQLError as exc:
            errors.append(f"{side}: could not check the workspace's server ({exc}).")
            continue
        if not on_this_server:
            errors.append(
                NOT_ON_THIS_SERVER_ERROR.format(side=side, slug=endpoint.slug)
            )
    if not target.slug and not _organization_is_on_this_server(target.organization_id):
        errors.append(
            f"target: organization '{target.organization_id}' is not on this "
            "server, so it cannot be copied as a same-server copy."
        )
    return errors


def _target_permission_errors(target: Endpoint) -> list[str]:
    """Refuse a target workspace the token's user cannot edit.

    The same-server copies write the database and static web apps directly,
    without the permission checks GraphQL applies, so the check is made here.
    A new target is created by the token's user, who can edit it.
    """
    if target.workspace is None or target.workspace.permissions.update:
        return []
    return [
        f"target: this token cannot edit workspace '{target.slug}' (it needs "
        "the editor role or above)."
    ]


def _build_remote_client(side: str, url: str, token: str) -> Client:
    """Build and authenticate an SDK client (used by the template flow).

    Templates are copied between two different servers, so a blank URL is itself
    an error — raised here so :func:`_verify_side` records it like any other
    verification failure.
    """
    if not url:
        raise GraphQLError(f"{side} server URL is required.")
    return build_client(url, token, label=side)


def _verify_side(side: str, build: Callable[[], Any]) -> tuple[Any | None, str | None]:
    """Build one endpoint (or client), returning ``(value, error_message)``.

    Building an endpoint/client authenticates against its server, so this
    is also where bad credentials / unreachable hosts surface. The returned
    string is the user-facing reason; ``None`` means the side is good.
    """
    try:
        return build(), None
    except GraphQLError as exc:
        # build_client already labels authentication failures with the side.
        return None, str(exc)
    except httpx.HTTPError as exc:
        return None, f"{side} server is unreachable ({exc.__class__.__name__})."


def _verify_endpoints(
    *,
    source_url: str | None,
    source_token: str | None,
    source_slug: str,
    target_url: str | None,
    target_token: str | None,
    target_organization_id: str | None,
    target_workspace_name: str | None,
    target_workspace_slug: str | None = None,
    same_server: bool = False,
) -> tuple[Endpoint, Endpoint]:
    """Verify and build both endpoints, raising :class:`CredentialError` on failure."""
    source, source_err = _verify_side(
        "source",
        lambda: _build_source(source_url, source_token, source_slug),
    )
    target, target_err = _verify_side(
        "target",
        lambda: _build_target(
            target_url,
            target_token,
            target_organization_id,
            target_workspace_name,
            target_workspace_slug,
        ),
    )
    errors = [e for e in (source_err, target_err) if e]
    if same_server and not errors:
        errors = _same_server_errors(source, target) + _target_permission_errors(target)
    if errors:
        raise CredentialError(errors)
    return source, target


def run_copy(
    *,
    source_url: str | None,
    source_token: str | None,
    source_slug: str,
    target_url: str | None,
    target_token: str | None,
    target_organization_id: str | None,
    target_workspace_name: str | None = None,
    target_workspace_slug: str | None = None,
    resources: set[str] | None = None,
    options: CopyOptions = CopyOptions(),
    reporter: ProgressReporter,
    result: CopyResult | None = None,
) -> CopyResult:
    """Verify both endpoints, then copy the workspace, returning the result."""
    source, target = _verify_endpoints(
        source_url=source_url,
        source_token=source_token,
        source_slug=source_slug,
        target_url=target_url,
        target_token=target_token,
        target_organization_id=target_organization_id,
        target_workspace_name=target_workspace_name,
        target_workspace_slug=target_workspace_slug,
        same_server=options.same_server,
    )
    return copy_workspace(
        source,
        target,
        reporter,
        resources=resources,
        options=options,
        result=result,
    )


def run_template_copy(
    *,
    source_url: str,
    source_token: str,
    target_url: str,
    target_token: str,
    target_organization_id: str,
    reporter: ProgressReporter,
) -> TemplatesResult:
    """Verify both endpoints, then copy every template, returning the result.

    Both sides are checked even if the first fails, so the user sees every
    problem at once. ``target_organization_id`` is the organization the host
    "Template pipelines" workspace is created under on the target.
    """
    source, source_err = _verify_side(
        "source", lambda: _build_remote_client("source", source_url, source_token)
    )
    target, target_err = _verify_side(
        "target", lambda: _build_remote_client("target", target_url, target_token)
    )
    errors = [e for e in (source_err, target_err) if e]
    if errors:
        raise CredentialError(errors)
    return copy_templates(
        source,
        target,
        target_organization_id=target_organization_id,
        reporter=reporter,
    )
