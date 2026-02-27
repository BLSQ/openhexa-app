import json
import uuid

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from oauth2_provider.models import Application
from oauth2_provider.views import AuthorizationView

from hexa.mcp.server import get_tools_list


def get_base_url(request: HttpRequest) -> str:
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
    base_url = get_base_url(request)
    return JsonResponse(
        {
            "resource": f"{base_url}/mcp/",
            "authorization_servers": [base_url],
            "scopes_supported": ["openhexa:mcp"],
            "bearer_methods_supported": ["header"],
        }
    )


def _server_metadata(request: HttpRequest) -> dict:
    base_url = get_base_url(request)
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize/",
        "token_endpoint": f"{base_url}/oauth/token/",
        "registration_endpoint": f"{base_url}/oauth/register/",
        "scopes_supported": ["openhexa:mcp"],
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
@require_POST
def dynamic_client_registration(request: HttpRequest) -> JsonResponse:
    """RFC 7591 — Dynamic Client Registration."""
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


@method_decorator(csrf_exempt, name="dispatch")
class OAuthAuthorizeView(AuthorizationView):
    login_url = "/login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scopes = self.request.GET.get("scope", "")
        if "openhexa:mcp" in scopes.split():
            context["tools"] = [
                {"name": t["name"], "description": t.get("description", "")}
                for t in get_tools_list()
            ]
        return context
