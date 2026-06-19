"""Shared entry point for the workspace duplication flows (CLI + admin).

Builds source/target :class:`Endpoint`s from raw connection parameters and runs
the orchestrator. This is the single place both the management command and the
admin view call, so neither holds any orchestration logic — they stay dumb
wrappers around :func:`run_migration`.

A blank server URL means the *local* server (ORM); a URL means a remote server
reached over GraphQL after a superuser login.
"""

from hexa.workspace_duplicator.endpoints import Endpoint
from hexa.workspace_duplicator.orchestrator import duplicate_workspace
from hexa.workspace_duplicator.results import DuplicationResult
from hexa.workspace_duplicator.transport import build_client
from hexa.workspaces.models import Workspace


def _build_source(
    url: str | None, email: str | None, password: str | None, slug: str
) -> Endpoint:
    if url:
        client = build_client(url, email, password, label="source")
        return Endpoint.remote(client, slug)
    return Endpoint.local(slug, workspace=Workspace.objects.get(slug=slug))


def _build_target(
    url: str | None,
    email: str | None,
    password: str | None,
    organization_id: str | None,
) -> Endpoint:
    if url:
        client = build_client(url, email, password, label="target")
        return Endpoint.remote(client, organization_id=organization_id)
    return Endpoint.local(organization_id=organization_id)


def run_migration(
    *,
    source_url: str | None,
    source_email: str | None,
    source_password: str | None,
    source_slug: str,
    target_url: str | None,
    target_email: str | None,
    target_password: str | None,
    target_organization_id: str | None = None,
    resources: set[str] | None = None,
) -> DuplicationResult:
    """Build both endpoints and duplicate the workspace, returning the result."""
    source = _build_source(source_url, source_email, source_password, source_slug)
    target = _build_target(
        target_url, target_email, target_password, target_organization_id
    )
    return duplicate_workspace(source, target, resources=resources)
