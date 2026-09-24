from ariadne import QueryType
from django.db.models import Exists, OuterRef, Q
from django.http import HttpRequest
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application, RefreshToken

from hexa.mcp.models import MCPConnection
from hexa.mcp.protocol import get_tools_catalogue

mcp_queries = QueryType()


@mcp_queries.field("mcpConnections")
def resolve_mcp_connections(_, info):
    request: HttpRequest = info.context["request"]
    live_token = AccessToken.objects.filter(
        user=OuterRef("user"),
        application=OuterRef("application"),
        expires__gt=timezone.now(),
    )
    live_refresh = RefreshToken.objects.filter(
        user=OuterRef("user"),
        application=OuterRef("application"),
        revoked__isnull=True,
    )
    return (
        MCPConnection.objects.filter(user=request.user)
        .annotate(has_token=Exists(live_token), has_refresh=Exists(live_refresh))
        .filter(Q(has_token=True) | Q(has_refresh=True))
        .select_related("application")
    )


@mcp_queries.field("mcpAuthorizationRequest")
def resolve_mcp_authorization_request(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        application = Application.objects.get(client_id=kwargs["client_id"])
    except Application.DoesNotExist:
        return None

    return {
        "client_name": application.name,
        "connection": MCPConnection.objects.filter(
            user=request.user, application=application
        ).first(),
        "tools": get_tools_catalogue(),
    }


@mcp_queries.field("mcpTools")
def resolve_mcp_tools(_, info):
    return get_tools_catalogue()


bindables = [mcp_queries]
