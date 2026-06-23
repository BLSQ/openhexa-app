"""GraphQL transport: SDK-backed clients, error type, request wrapper."""

from typing import Any

import httpx
from openhexa.graphql.graphql_client.client import Client
from openhexa.graphql.graphql_client.exceptions import GraphQLClientError


class GraphQLError(RuntimeError):
    pass


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


def build_client(server_url: str, email: str, password: str, *, label: str) -> Client:
    """Authenticate against an OpenHEXA server via the GraphQL Login mutation.

    `label` is used only to make the error message ("source"/"target") clearer.
    """
    # 120s read timeout: createPipelineTemplateVersion can fan out to
    # auto-update every pipeline derived from the template, which is slow
    # on prod and exceeds httpx's 5s default.
    http = httpx.Client(
        headers={"User-Agent": "openhexa-migrate/1.0"},
        timeout=httpx.Timeout(120.0),
    )
    # Prime CSRF cookie. Defensive — GraphQLView is csrf_exempt on the
    # current backend, but a future change would otherwise silently
    # break every mutation.
    http.get(server_url)
    csrf = http.cookies.get("csrftoken")
    if csrf:
        http.headers["X-CSRFToken"] = csrf
        http.headers["Referer"] = server_url

    client = Client(url=server_url, http_client=http)
    data = gql(
        client,
        "mutation Login($input: LoginInput!) { login(input: $input) { success errors } }",
        {"input": {"email": email, "password": password}},
        "Login",
    )
    if not data["login"]["success"]:
        raise GraphQLError(
            f"{label} login failed: " + ",".join(data["login"]["errors"] or [])
        )
    return client
