from functools import cache
from typing import Callable

from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

ANONYMOUS_URLS = [
    reverse("logout"),
    reverse("core:index"),
    reverse("core:ready"),
    reverse("notebooks:credentials"),
    reverse("graphql"),
    reverse("password_reset"),
    reverse("password_reset_done"),
    reverse("user:accept_tos"),
]
ANONYMOUS_PREFIXES = ["/auth/reset/"]


@cache
def is_protected_routes(url: str) -> bool:
    """
    Is the URL should be behind login screen? Must the user accept the TOS to get this page?
    """
    global ANONYMOUS_URLS, ANONYMOUS_PREFIXES

    matches_prefix = False
    for prefix in ANONYMOUS_PREFIXES:
        if url.startswith(prefix):
            matches_prefix = True

    return not (matches_prefix or (url in ANONYMOUS_URLS))


def login_required_middleware(
    get_response: Callable[[HttpRequest], HttpResponse]
) -> Callable[[HttpRequest], HttpResponse]:
    """Authentication is mandatory for all routes except logout, index and ready endpoint."""

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
        # FIXME exclude logout, is_ready,
        if (
            request.user.is_authenticated
            and is_protected_routes(request.path)
            and not request.user.accepted_tos
            and settings.USER_MUST_ACCEPT_TOS
        ):
            return render(request, "user_management/terms_of_service.html")
        else:
            return get_response(request)

    return middleware
