import json

from ariadne_django.views import GraphQLView
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from graphql import OperationDefinitionNode
from graphql import parse as gql_parse

from config.schema import schema
from hexa.analytics.api import track
from hexa.webapps.authentication import WebappUser
from hexa.webapps.models import Webapp
from hexa.webapps.scopes import fields_allowed_by

INTROSPECTION_FIELDS = {"__typename", "__schema", "__type"}


def extract_top_level_fields(query_string: str) -> set[str]:
    document = gql_parse(query_string)
    return {
        selection.name.value
        for definition in document.definitions
        if isinstance(definition, OperationDefinitionNode)
        for selection in definition.selection_set.selections
        if hasattr(selection, "name")
    }


_graphql_view = GraphQLView.as_view(schema=schema)


def _check_origin(request: HttpRequest) -> bool:
    origin = request.META.get("HTTP_ORIGIN", "")
    if not origin:
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
        requested_fields = extract_top_level_fields(query_string)
    except Exception:
        return JsonResponse(
            {
                "errors": [
                    {"message": "Impossible to parse the query for top-level fields"}
                ]
            },
            status=400,
        )

    requested_fields -= INTROSPECTION_FIELDS
    allowed_fields = fields_allowed_by(webapp.allowed_operations)
    disallowed = requested_fields - allowed_fields

    event_properties = {
        "webapp_id": str(webapp.id),
        "webapp_name": webapp.name,
        "workspace_id": str(webapp.workspace_id),
        "workspace_name": webapp.workspace.name,
        "is_public": webapp.is_public,
        "operations": sorted(requested_fields),
    }

    if disallowed:
        track(
            request,
            "webapp_graphql_query",
            {
                **event_properties,
                "status": "denied",
                "disallowed_operations": sorted(disallowed),
            },
        )
        return JsonResponse(
            {
                "errors": [
                    {
                        "message": f"Operations not allowed: {', '.join(sorted(disallowed))}"
                    }
                ]
            },
            status=403,
        )

    track(request, "webapp_graphql_query", {**event_properties, "status": "allowed"})

    # Wrap the request user as a WebappUser so every downstream resolver sees a
    # principal whose accessible workspaces/orgs are already scoped to this
    # webapp and whose has_perm is gated by allowed_operations. Public webapps
    # carry no real user — the proxy hard-scopes to the webapp's workspace.
    session_user = request.user if request.user.is_authenticated else None
    request.user = WebappUser(webapp=webapp, real_user=session_user)
    return _graphql_view(request)
