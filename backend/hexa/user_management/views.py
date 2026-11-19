import requests
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from sentry_sdk import capture_exception

from hexa.analytics.api import track

from .utils import get_login_link_target


class LogoutView(BaseLogoutView):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            hub_response = requests.get(
                f"{settings.NOTEBOOKS_HUB_URL}/logout",
                cookies={
                    settings.SESSION_COOKIE_NAME: request.session.session_key,
                    settings.CSRF_COOKIE_NAME: get_token(request),
                },
                allow_redirects=False,
            )
            hub_response.raise_for_status()
        except requests.HTTPError as e:
            capture_exception(e)
        finally:
            return super().post(request, *args, **kwargs)


def login_link(request: HttpRequest, token: str) -> HttpResponse:
    """Log in the owner created by ``createOrganization`` (see ``get_login_url``) and open their organization."""
    target = get_login_link_target(token)
    if target is None:
        return redirect(f"{settings.NEW_FRONTEND_DOMAIN}/login")
    user, organization_id = target
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    track(request, "users.user_logged_in", user=user)
    return redirect(f"{settings.NEW_FRONTEND_DOMAIN}/organizations/{organization_id}")
