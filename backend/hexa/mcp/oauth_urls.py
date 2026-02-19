from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.views import AuthorizationView


@method_decorator(csrf_exempt, name="dispatch")
class OAuthAuthorizeView(AuthorizationView):
    login_url = "/mcp/login/"


urlpatterns = [
    path("authorize/", OAuthAuthorizeView.as_view(), name="oauth2_authorize"),
]
