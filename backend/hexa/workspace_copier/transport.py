"""GraphQL transport: SDK-backed clients, error type, request wrapper."""

from typing import Any

import httpx
from django.conf import settings
from openhexa.graphql.graphql_client.client import Client
from openhexa.graphql.graphql_client.exceptions import GraphQLClientError


class GraphQLError(RuntimeError):
    pass


def _route_to_internal_url(request: httpx.Request) -> None:
    """Send requests aimed at this server's public URL to its internal one.

    The copy runs in the worker container, where the public ``BASE_URL``
    (``http://localhost:8000`` locally) points to the worker itself, not the
    app. That covers both a copy to/from this server and the presigned file
    links this server hands out, which are built from ``BASE_URL`` on the
    filesystem storage backend. In production both settings are usually equal,
    so this is a no-op.
    """
    public = httpx.URL(settings.BASE_URL)
    internal = httpx.URL(settings.INTERNAL_BASE_URL)
    if public == internal:
        return
    url = request.url
    if (url.scheme, url.host, url.port) == (public.scheme, public.host, public.port):
        request.url = url.copy_with(
            scheme=internal.scheme, host=internal.host, port=internal.port
        )


def build_http_client(**kwargs: Any) -> httpx.Client:
    """An httpx client that reaches this server even from the worker container."""
    return httpx.Client(event_hooks={"request": [_route_to_internal_url]}, **kwargs)


def gql(
    client: Client,
    query: str,
    variables: dict[str, Any] | None = None,
    operation_name: str | None = None,
) -> dict[str, Any]:
    """Execute a raw GraphQL query through the SDK client and return data."""
    resp = client.execute(
        query=query, variables=variables or {}, operation_name=operation_name
    )
    if not resp.is_success:
        # Surface the body — the SDK's __str__ only shows the status code,
        # which loses the actual GraphQL/Django error.
        raise GraphQLError(
            f"{operation_name or '<anon>'} returned HTTP {resp.status_code}: "
            f"{resp.text[:2000]}"
        )
    try:
        # A 200 response can still carry a top-level `errors` array (any
        # resolver exception or query error). get_data raises the SDK's
        # GraphQLClientError in that case, which the module's callers expect
        # as our GraphQLError — translate it here so a single server-side
        # error is recorded per-item instead of aborting the whole copy.
        return client.get_data(resp)
    except GraphQLClientError as exc:
        raise GraphQLError(
            f"{operation_name or '<anon>'} GraphQL error: {exc}"
        ) from exc


def build_client(
    server_url: str,
    token: str,
    *,
    label: str,
    http_client: httpx.Client | None = None,
) -> Client:
    """Build an SDK client authenticated with a Bearer token and verify it.

    The token is a ServiceAccount token, which the backend authenticates per
    request via the ``Authorization: Bearer`` header — so there is no login
    round-trip or session cookie to manage. A cheap ``me`` query is run up front
    so an invalid or under-permissioned token surfaces here rather than mid-copy.

    `label` is used only to make the error message ("source"/"target") clearer.
    `http_client` lets tests inject a transport (e.g. WSGI) routed at the
    in-process app; in production it is built here.
    """
    # 120s read timeout: createPipelineTemplateVersion can fan out to
    # auto-update every pipeline derived from the template, which is slow
    # on prod and exceeds httpx's 5s default.
    http = http_client or build_http_client(timeout=httpx.Timeout(120.0))
    http.headers["User-Agent"] = "openhexa-copy/1.0"
    http.headers["Authorization"] = f"Bearer {token}"

    client = Client(url=server_url, http_client=http)
    data = gql(client, "query Me { me { user { id } } }", operation_name="Me")
    if not (data.get("me") or {}).get("user"):
        raise GraphQLError(
            f"{label} authentication failed: the token is invalid or lacks access."
        )
    return client
