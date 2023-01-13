import logging
from functools import cache
from typing import Callable

from django.apps import apps
from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django_otp.middleware import OTPMiddleware

from hexa.app import get_hexa_app_configs

from .utils import has_configured_two_factor

logger = logging.getLogger(__name__)


@cache
def get_anonymous_urls():
    anonymous_urls = []

    for app_config in get_hexa_app_configs():
        anonymous_urls += getattr(app_config, "ANONYMOUS_URLS", [])

    return [reverse(url) for url in anonymous_urls]


@cache
def get_anonymous_prefixes():
    # We don't have an app config for the GraphQL url itself - it is defined in the core urls module
    anonymous_prefixes = ["/auth/reset/", "/graphql/"]
    for app_config in apps.get_app_configs():
        anonymous_prefixes += getattr(app_config, "ANONYMOUS_PREFIXES", [])

    return anonymous_prefixes


@cache
def is_protected_routes(url: str) -> bool:
    """
    Is the URL should be behind login screen? Must the user accept the TOS to get this page?
    """
    matches_prefix = False
    for prefix in get_anonymous_prefixes():
        if url.startswith(prefix):
            matches_prefix = True

    return not (matches_prefix or (url in get_anonymous_urls()))


def login_required_middleware(
    get_response: Callable[[HttpRequest], HttpResponse]
) -> Callable[[HttpRequest], HttpResponse]:
    """Authentication by cookie is mandatory for all routes except the ones specified in
    the app configs ANONYMOUS_PREFIXES and ANONYMOUS_URLS.
    Mostly: logout, index, ready and some API endpoints (that implement their own authentication)"""

    def middleware(request: HttpRequest) -> HttpResponse:
        if not is_protected_routes(request.path):
            return get_response(request)

        if not request.user.is_authenticated or (
            has_configured_two_factor(request.user) and not request.user.is_verified()
        ):
            return redirect(
                "{}?next={}".format(reverse(settings.LOGIN_URL), request.path)
            )

        return get_response(request)

    return middleware


def accepted_tos_required_middleware(
    get_response: Callable[[HttpRequest], HttpResponse]
) -> Callable[[HttpRequest], HttpResponse]:
    """
    TOS is mandatory for all:
        - authenticated user
        - except routes logout, index and ready endpoint.
    """

    def middleware(request: HttpRequest) -> HttpResponse:
        if (
            request.user.is_authenticated
            and is_protected_routes(request.path)
            and not getattr(request.user, "accepted_tos", False)
            and settings.USER_MUST_ACCEPT_TOS
        ):
            return render(request, "user_management/terms_of_service.html")
        else:
            return get_response(request)

    return middleware


class TwoFactorMiddleware(OTPMiddleware):
    """
    This must be installed after
    :class:`~django.contrib.auth.middleware.AuthenticationMiddleware`.
    """
