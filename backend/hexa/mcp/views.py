import logging

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from hexa.oauth.views import get_base_url

logger = logging.getLogger(__name__)


def tools_json(request: HttpRequest) -> JsonResponse:
    """Returns the list of MCP tools as JSON for the frontend."""
    from .server import (
        MCP_SERVER_NAME,
        MCP_SERVER_VERSION,
        PROTOCOL_VERSION,
        get_tools_list,
    )

    return JsonResponse(
        {
            "server_name": MCP_SERVER_NAME,
            "server_version": MCP_SERVER_VERSION,
            "protocol_version": PROTOCOL_VERSION,
            "tools": get_tools_list(),
        }
    )


@csrf_exempt
def mcp_endpoint(request: HttpRequest) -> HttpResponse:
    """Main MCP endpoint. Handles JSON-RPC 2.0 messages from MCP clients."""
    if request.method == "GET":
        return tools_json(request)

    if request.method == "DELETE":
        return HttpResponse(status=200)

    if request.method != "POST":
        return HttpResponse(status=405)

    if not request.user.is_authenticated:
        response = JsonResponse(
            {
                "error": "unauthorized",
                "error_description": "Bearer token required",
            },
            status=401,
        )
        base_url = get_base_url(request)
        response[
            "WWW-Authenticate"
        ] = f'Bearer resource_metadata="{base_url}/.well-known/oauth-protected-resource"'
        return response

    from .server import handle_jsonrpc

    result = handle_jsonrpc(request.body, request.user)

    if result is None:
        return HttpResponse(status=204)

    response = JsonResponse(result, status=200)
    response["Content-Type"] = "application/json"
    return response
