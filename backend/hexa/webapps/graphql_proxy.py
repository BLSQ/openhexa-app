import hashlib
import json

import sentry_sdk
from ariadne_django.views import GraphQLView
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, JsonResponse
from graphql import GraphQLError
from graphql import parse as gql_parse

from config.schema import schema
from hexa.analytics.api import track
from hexa.webapps.models import Webapp
from hexa.webapps.scopes import ungrantable_fields
from hexa.webapps.utils import is_local_dev_origin, is_preview_host

_graphql_view = GraphQLView.as_view(schema=schema)

SENTRY_DENIAL_REPORT_INTERVAL = 60 * 60


def _check_origin(request: HttpRequest) -> bool:
    origin = request.META.get("HTTP_ORIGIN", "")
    if not origin:
        return True
    if is_preview_host(request.get_host()) and is_local_dev_origin(origin):
        return True
    request_origin = f"{settings.SCHEME}://{request.get_host()}"
    return origin.rstrip("/") == request_origin.rstrip("/")


def _should_report_denial(
    request: HttpRequest, webapp: Webapp, denied: list[str]
) -> bool:
    # Preview hosts serve web apps under development, where denials are part of
    # writing the queries rather than a live web app breaking.
    if is_preview_host(request.get_host()):
        return False
    # A broken web app is denied on every request of every viewer, so each web app
    # and set of fields is reported at most once per interval. No shared cache is
    # configured, so the limit holds per process: an upper bound, not an exact count.
    fields_hash = hashlib.sha256(",".join(denied).encode()).hexdigest()
    key = f"webapp-graphql-denied:{webapp.id}:{fields_hash}"
    return cache.add(key, True, timeout=SENTRY_DENIAL_REPORT_INTERVAL)


def _report_denied_to_sentry(
    webapp: Webapp, denied: list[str], missing_scopes: list[str]
) -> None:
    # A denial usually means a live web app is broken for its viewers, so it is
    # reported as an issue (one per web app and set of fields) rather than only tracked.
    # `not_grantable` denials need a change on our side (or are a web app probing
    # for secrets); `missing_scope` ones are fixed by the owner enabling a scope.
    ungrantable = sorted(ungrantable_fields(denied))
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("webapp_id", str(webapp.id))
        scope.set_tag("workspace_slug", webapp.workspace.slug)
        scope.set_tag("webapp_is_public", webapp.is_public)
        scope.set_tag(
            "denial_kind", "not_grantable" if ungrantable else "missing_scope"
        )
        scope.set_context(
            "webapp_graphql_denied",
            {
                "denied_fields": denied,
                "ungrantable_fields": ungrantable,
                "enabled_scopes": sorted(webapp.allowed_operations),
                "missing_scopes": missing_scopes,
            },
        )
        scope.fingerprint = ["webapp-graphql-denied", str(webapp.id), *denied]
        sentry_sdk.capture_message(
            f"Webapp GraphQL fields not allowed: {', '.join(denied)}",
            level="warning",
        )


def handle_graphql_proxy(request: HttpRequest, webapp: Webapp):
    if request.method != "POST":
        return JsonResponse(
            {"errors": [{"message": "Only POST requests are supported"}]},
            status=405,
        )

    if not _check_origin(request):
        return JsonResponse(
            {"errors": [{"message": "Origin not allowed"}]},
            status=403,
        )

    try:
        body = json.loads(request.body)
        query_string = body.get("query", "")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"errors": [{"message": "Invalid request body"}]},
            status=400,
        )

    if not query_string:
        return JsonResponse(
            {"errors": [{"message": "No query provided"}]},
            status=400,
        )

    try:
        document = gql_parse(query_string)
    except GraphQLError:
        return JsonResponse(
            {"errors": [{"message": "Impossible to parse the query"}]},
            status=400,
        )

    scope_check = webapp.scope_policy.check(document)

    event_properties = {
        "webapp_id": str(webapp.id),
        "webapp_name": webapp.name,
        "workspace_id": str(webapp.workspace_id),
        "workspace_name": webapp.workspace.name,
        "is_public": webapp.is_public,
        "operations": sorted(scope_check.operations),
    }

    if scope_check.denied:
        denied = sorted(scope_check.denied)
        missing_scopes = sorted(webapp.scope_policy.missing_scopes(denied))
        track(
            request,
            "webapp_graphql_query",
            {
                **event_properties,
                "status": "denied",
                "disallowed_operations": denied,
            },
        )
        if _should_report_denial(request, webapp, denied):
            _report_denied_to_sentry(webapp, denied, missing_scopes)
        message = f"Fields not allowed: {', '.join(denied)}"
        if missing_scopes:
            message += f". Enable scope(s): {', '.join(missing_scopes)}"
        return JsonResponse({"errors": [{"message": message}]}, status=403)

    track(request, "webapp_graphql_query", {**event_properties, "status": "allowed"})
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("webapp_graphql", True)
        return _graphql_view(request)
