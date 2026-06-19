"""GraphQL transport: SDK-backed clients, error type, request wrapper, debug."""

import logging
import sys
from contextlib import contextmanager
from typing import Any

import httpx
from openhexa.graphql.graphql_client.client import Client

# Module-global so the gql() wrapper and the SDK-call helpers don't need to
# thread it through every signature. Toggle it via debug_logging() rather than
# assigning directly, so the httpx/httpcore wire logging moves in lockstep and
# the change is always restored afterwards.
DEBUG = False

# The SDK's httpx client logs every request/connection; these libraries are the
# source of the connect_tcp/start_tls/HTTP-request noise, gated behind --debug.
_HTTP_LOGGERS = ("httpx", "httpcore")


def _dbg(msg: str) -> None:
    if DEBUG:
        sys.stderr.write(f"[debug] {msg}\n")


@contextmanager
def debug_logging(enabled: bool):
    """Toggle GraphQL + httpx/httpcore debug logging for the block, then restore.

    Both entry points use this so the toggle behaves identically. It matters
    most for the admin view: that runs in a long-lived process, so a bare
    assignment to ``DEBUG`` (or a logger level) would leak into later requests.
    """
    global DEBUG
    loggers = {name: logging.getLogger(name) for name in _HTTP_LOGGERS}
    prev_debug = DEBUG
    prev_levels = {name: lg.level for name, lg in loggers.items()}

    DEBUG = enabled
    level = logging.DEBUG if enabled else logging.WARNING
    for lg in loggers.values():
        lg.setLevel(level)
    try:
        yield
    finally:
        DEBUG = prev_debug
        for name, lg in loggers.items():
            lg.setLevel(prev_levels[name])


def _short(value: Any, limit: int = 200) -> str:
    """Render a value for debug output without dumping huge zipfiles."""
    if isinstance(value, dict):
        return (
            "{" + ", ".join(f"{k}={_short(v, limit)}" for k, v in value.items()) + "}"
        )
    if isinstance(value, list):
        head = ", ".join(_short(v, limit) for v in value[:3])
        return f"[{head}{', ...' if len(value) > 3 else ''}] (n={len(value)})"
    s = repr(value)
    return (
        s if len(s) <= limit else s[:limit] + f"... <truncated {len(s) - limit} chars>"
    )


class GraphQLError(RuntimeError):
    pass


def gql(
    client: Client,
    query: str,
    variables: dict[str, Any] | None = None,
    operation_name: str | None = None,
) -> dict[str, Any]:
    """Execute a raw GraphQL query through the SDK client and return data."""
    if DEBUG:
        _dbg(f"-> {operation_name or '<anon>'} @ {client.url}")
        _dbg(f"   variables: {_short(variables or {})}")
    resp = client.execute(
        query=query, variables=variables or {}, operation_name=operation_name
    )
    if DEBUG:
        _dbg(f"<- HTTP {resp.status_code} ({len(resp.content)} bytes)")
    if not resp.is_success:
        # Surface the body — the SDK's __str__ only shows the status code,
        # which loses the actual GraphQL/Django error.
        raise GraphQLError(
            f"{operation_name or '<anon>'} returned HTTP {resp.status_code}: "
            f"{resp.text[:2000]}"
        )
    return client.get_data(resp)


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
