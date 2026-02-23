from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.views import AuthorizationView


@method_decorator(csrf_exempt, name="dispatch")
class OAuthAuthorizeView(AuthorizationView):
    login_url = "/login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from hexa.mcp.server import get_tools_list

        context["tools"] = [
            {"name": t["name"], "description": t.get("description", "")}
            for t in get_tools_list()
        ]
        return context


urlpatterns = [
    path("authorize/", OAuthAuthorizeView.as_view(), name="oauth2_authorize"),
]
