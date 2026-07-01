"""Shared entry point for the workspace copy flows (CLI + admin).

Builds source/target :class:`Endpoint`s from raw connection parameters and runs
the orchestrator. This is the single place both the management command and the
admin view call, so neither holds any orchestration logic — they stay dumb
wrappers around :func:`run_copy`.

A blank server URL means the *local* server (ORM); a URL means a remote server
reached over GraphQL with a ServiceAccount Bearer token.

Every run starts with a verification step that builds both endpoints up front —
which, for a remote side, authenticates against its server. Both sides are
checked even if the first fails, so the user sees every problem at once rather
than fixing them one round-trip at a time.
"""

from collections.abc import Callable
from typing import Any

import httpx
from django.core.exceptions import ObjectDoesNotExist
from openhexa.graphql.graphql_client.client import Client

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.orchestrator import copy_workspace
from hexa.workspace_copier.progress import ProgressReporter
from hexa.workspace_copier.results import CopyResult, TemplatesResult
from hexa.workspace_copier.templates import copy_templates
from hexa.workspace_copier.transport import GraphQLError, build_client
from hexa.workspaces.models import Workspace


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
    if url:
        client = build_client(url, token, label="source")
        return Endpoint.remote(client, slug)
    return Endpoint.local(slug, workspace=Workspace.objects.get(slug=slug))


def _build_target(
    url: str | None,
    token: str | None,
    organization_id: str | None,
    workspace_name: str | None,
    workspace_slug: str | None,
) -> Endpoint:
    if workspace_slug:
        return _build_existing_target(url, token, workspace_slug)
    if url:
        client = build_client(url, token, label="target")
        return Endpoint.remote(
            client, organization_id=organization_id, workspace_name=workspace_name
        )
    return Endpoint.local(
        organization_id=organization_id, workspace_name=workspace_name
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
    if url:
        client = build_client(url, token, label="target")
        if client.workspace(slug=workspace_slug) is None:
            raise GraphQLError(
                f"target workspace '{workspace_slug}' not found — create it first "
                "or omit --target-workspace-slug to create a new workspace."
            )
        return Endpoint.remote(client, slug=workspace_slug)
    return Endpoint.local(
        slug=workspace_slug,
        workspace=Workspace.objects.get(slug=workspace_slug),
    )


def _build_remote_client(side: str, url: str, token: str) -> Client:
    """Build and authenticate a remote SDK client (used by the template flow).

    The template copy flow is remote→remote only (templates are server-wide and
    the local/ORM path is not implemented), so a blank URL is itself an error —
    raised here so :func:`_verify_side` records it like any other verification
    failure.
    """
    if not url:
        raise GraphQLError(f"{side} server URL is required.")
    return build_client(url, token, label=side)


def _verify_side(side: str, build: Callable[[], Any]) -> tuple[Any | None, str | None]:
    """Build one endpoint (or client), returning ``(value, error_message)``.

    Building a remote endpoint/client authenticates against its server, so this
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
    except ObjectDoesNotExist as exc:
        return None, f"{side}: {exc}"


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
    reporter: ProgressReporter,
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
    )
    return copy_workspace(source, target, reporter, resources=resources)


def run_template_copy(
    *,
    source_url: str,
    source_token: str,
    target_url: str,
    target_token: str,
    target_organization_id: str,
    reporter: ProgressReporter,
) -> TemplatesResult:
    """Verify both remote endpoints, then copy every template, returning the result.

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
