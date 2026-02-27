import logging

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt

from hexa.oauth.views import get_base_url

logger = logging.getLogger(__name__)


def tools_page(request: HttpRequest) -> TemplateResponse:
    """Public page listing all MCP tools and their schemas."""
    from .server import (
        MCP_SERVER_NAME,
        MCP_SERVER_VERSION,
        PROTOCOL_VERSION,
        get_tools_list,
    )

    raw_tools = get_tools_list()
    tools = []
    for t in raw_tools:
        schema = t.get("inputSchema", {})
        properties = schema.get("properties", {})
        required_set = set(schema.get("required", []))
        params = [
            {
                "name": name,
                "type": prop.get("type", "string"),
                "required": name in required_set,
            }
            for name, prop in properties.items()
        ]
        tools.append(
            {
                "name": t["name"],
                "description": t.get("description", ""),
                "params": params,
                "param_count": len(params),
            }
        )

    return TemplateResponse(
        request,
        "mcp/tools.html",
        {
            "tools": tools,
            "server_name": MCP_SERVER_NAME,
            "server_version": MCP_SERVER_VERSION,
            "protocol_version": PROTOCOL_VERSION,
        },
    )


@csrf_exempt
def mcp_endpoint(request: HttpRequest) -> HttpResponse:
    """Main MCP endpoint. Handles JSON-RPC 2.0 messages from MCP clients."""
    if request.method == "GET":
        return tools_page(request)

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
