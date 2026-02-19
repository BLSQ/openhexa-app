import json
import logging
import uuid

from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


def _get_base_url(request: HttpRequest) -> str:
    """Build the base URL from the incoming request so it matches the public-facing host."""
    scheme = "https" if request.is_secure() else request.scheme
    host = request.get_host()
    if request.headers.get("X-Forwarded-Proto") == "https":
        scheme = "https"
    if request.headers.get("X-Forwarded-Host"):
        host = request.headers["X-Forwarded-Host"]
    return f"{scheme}://{host}"


def protected_resource_metadata(request: HttpRequest) -> JsonResponse:
    """RFC 9728 — OAuth Protected Resource Metadata."""
    base_url = _get_base_url(request)
    return JsonResponse(
        {
            "resource": f"{base_url}/mcp/",
            "authorization_servers": [base_url],
            "scopes_supported": ["read", "write"],
            "bearer_methods_supported": ["header"],
        }
    )


def _server_metadata(request: HttpRequest) -> dict:
    base_url = _get_base_url(request)
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize/",
        "token_endpoint": f"{base_url}/oauth/token/",
        "registration_endpoint": f"{base_url}/mcp/register/",
        "scopes_supported": ["read", "write"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": [
            "client_secret_basic",
            "client_secret_post",
            "none",
        ],
    }


def oauth_server_metadata(request: HttpRequest) -> JsonResponse:
    """RFC 8414 — OAuth Authorization Server Metadata."""
    return JsonResponse(_server_metadata(request))


def openid_configuration(request: HttpRequest) -> JsonResponse:
    """OpenID Connect Discovery — same metadata as RFC 8414 for compatibility."""
    return JsonResponse(_server_metadata(request))


@csrf_exempt
def oauth_login(request: HttpRequest):
    next_url = request.GET.get("next", "/")
    if request.user.is_authenticated:
        from django.shortcuts import redirect

        return redirect(next_url)

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            from django.shortcuts import redirect

            return redirect(request.POST.get("next", next_url))
    else:
        form = AuthenticationForm(request)

    return TemplateResponse(
        request,
        "mcp/login.html",
        {"form": form, "next": next_url},
    )


@csrf_exempt
@require_POST
def dynamic_client_registration(request: HttpRequest) -> JsonResponse:
    """RFC 7591 — Dynamic Client Registration."""
    from oauth2_provider.models import Application

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "invalid_request"}, status=400)

    redirect_uris = data.get("redirect_uris", [])
    client_name = data.get("client_name", "MCP Client")

    if not redirect_uris:
        return JsonResponse(
            {
                "error": "invalid_client_metadata",
                "error_description": "redirect_uris is required",
            },
            status=400,
        )

    client_id = uuid.uuid4().hex
    token_endpoint_auth_method = data.get("token_endpoint_auth_method", "none")

    if token_endpoint_auth_method == "none":
        client_type = Application.CLIENT_PUBLIC
        client_secret = ""
    else:
        client_type = Application.CLIENT_CONFIDENTIAL
        client_secret = uuid.uuid4().hex

    application = Application.objects.create(
        name=client_name,
        client_id=client_id,
        client_secret=client_secret,
        client_type=client_type,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        redirect_uris=" ".join(redirect_uris),
        skip_authorization=False,
    )

    response_data = {
        "client_id": application.client_id,
        "client_name": client_name,
        "redirect_uris": redirect_uris,
        "grant_types": ["authorization_code", "refresh_token"],
        "token_endpoint_auth_method": token_endpoint_auth_method,
    }
    if client_secret:
        response_data["client_secret"] = client_secret

    return JsonResponse(response_data, status=201)


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
        return JsonResponse(
            {
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "GET not supported, use POST"},
            },
            status=405,
        )

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
        base_url = _get_base_url(request)
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
