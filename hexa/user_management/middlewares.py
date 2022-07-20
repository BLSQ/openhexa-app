from functools import cache
from typing import Callable

from django.apps import apps
from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from hexa.plugins.app import get_hexa_app_configs

ANONYMOUS_URLS = [  # TODO: move to app configs
    "logout",
    "core:index",
    "core:ready",
    "notebooks:credentials",
    "graphql",
    "password_reset",
    "password_reset_done",
    "user:accept_tos",
]

# TODO: document
for app_config in get_hexa_app_configs():
    ANONYMOUS_URLS += getattr(app_config, "ANONYMOUS_URLS", [])
REVERSED_ANONYMOUS_URLS = [reverse(url) for url in ANONYMOUS_URLS]

ANONYMOUS_PREFIXES = ["/auth/reset/"]
for app_config in apps.get_app_configs():
    ANONYMOUS_PREFIXES += getattr(app_config, "ANONYMOUS_PREFIXES", [])


@cache
def is_protected_routes(url: str) -> bool:
    """
    Is the URL should be behind login screen? Must the user accept the TOS to get this page?
    """
    matches_prefix = False
    for prefix in ANONYMOUS_PREFIXES:
        if url.startswith(prefix):
            matches_prefix = True

    return not (matches_prefix or (url in REVERSED_ANONYMOUS_URLS))


def login_required_middleware(
    get_response: Callable[[HttpRequest], HttpResponse]
) -> Callable[[HttpRequest], HttpResponse]:
    """Authentication by cookie is mandatory for all routes except the ones specified in
    the app configs ANONYMOUS_PREFIXES and ANONYMOUS_URLS.
    Mostly: logout, index, ready and some API endpoints (that implement their own authentication)"""

    def middleware(request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated and is_protected_routes(request.path):
            return redirect("{}?next={}".format(reverse("core:index"), request.path))

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
