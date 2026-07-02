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

import httpx
from django.core.exceptions import ObjectDoesNotExist

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.orchestrator import copy_workspace
from hexa.workspace_copier.progress import ProgressReporter
from hexa.workspace_copier.results import CopyResult
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
    organization_id: str,
    workspace_name: str | None,
) -> Endpoint:
    if url:
        client = build_client(url, token, label="target")
        return Endpoint.remote(
            client, organization_id=organization_id, workspace_name=workspace_name
        )
    return Endpoint.local(
        organization_id=organization_id, workspace_name=workspace_name
    )


def _verify_side(
    side: str, build: Callable[[], Endpoint]
) -> tuple[Endpoint | None, str | None]:
    """Build one endpoint, returning ``(endpoint, error_message)``.

    Building a remote endpoint authenticates against its server, so this is also
    where bad credentials / unreachable hosts surface. The returned string is the
    user-facing reason; ``None`` means the side is good.
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
    target_organization_id: str,
    target_workspace_name: str | None,
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
    target_organization_id: str,
    target_workspace_name: str | None = None,
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
    )
    return copy_workspace(source, target, reporter, resources=resources)
