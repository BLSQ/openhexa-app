import logging
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from sentry_sdk import capture_exception

from hexa.analytics.api import track

from .utils import read_login_link

logger = logging.getLogger(__name__)


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
    """
    Log in the owner created by ``createOrganization`` (see ``get_login_url``) and open their organization.

    An expired or used link still leads to the organization, through the login page unless that owner is already
    logged in: they have the password they chose on the console.
    """
    link = read_login_link(token)
    if link is None:
        logger.warning("Invalid login link")
        return redirect(f"{settings.NEW_FRONTEND_DOMAIN}/login")
    organization_path = f"/organizations/{link.organization_id}"
    if link.usable:
        login(request, link.user, backend="django.contrib.auth.backends.ModelBackend")
        track(request, "users.user_logged_in", user=link.user)
    elif request.user != link.user:
        query = urlencode({"next": organization_path})
        return redirect(f"{settings.NEW_FRONTEND_DOMAIN}/login?{query}")
    return redirect(f"{settings.NEW_FRONTEND_DOMAIN}{organization_path}")
