import json

import sentry_sdk
from ariadne_django.views import GraphQLView
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from graphql import GraphQLError
from graphql import parse as gql_parse

from config.schema import schema
from hexa.analytics.api import track
from hexa.webapps.models import Webapp
from hexa.webapps.utils import is_local_dev_origin, is_preview_host

_graphql_view = GraphQLView.as_view(schema=schema)


def _check_origin(request: HttpRequest) -> bool:
    origin = request.META.get("HTTP_ORIGIN", "")
    if not origin:
        return True
    if is_preview_host(request.get_host()) and is_local_dev_origin(origin):
        return True
    request_origin = f"{settings.SCHEME}://{request.get_host()}"
    return origin.rstrip("/") == request_origin.rstrip("/")


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
        track(
            request,
            "webapp_graphql_query",
            {
                **event_properties,
                "status": "denied",
                "disallowed_operations": sorted(scope_check.denied),
            },
        )
        return JsonResponse(
            {
                "errors": [
                    {
                        "message": f"Fields not allowed: {', '.join(sorted(scope_check.denied))}"
                    }
                ]
            },
            status=403,
        )

    track(request, "webapp_graphql_query", {**event_properties, "status": "allowed"})
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("webapp_graphql", True)
        return _graphql_view(request)
