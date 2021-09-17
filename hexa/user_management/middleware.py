from functools import cache

from django.shortcuts import redirect
from django.urls import reverse


def login_required_middleware(get_response):
    """Authentication is mandatory for all routes except logout, index and ready endpoint."""

    @cache
    def anonymous_urls():
        return [
            reverse("logout"),
            reverse("core:index"),
            reverse("core:ready"),
            reverse("notebooks:credentials"),
            reverse("graphql"),
            reverse("password_reset"),
            reverse("password_reset_done"),
        ]

    anonymous_prefixes = ["/auth/reset/"]

    def middleware(request):
        matches_prefix = False
        for prefix in anonymous_prefixes:
            if request.path.startswith(prefix):
                matches_prefix = True

        requires_auth = request.path not in anonymous_urls() and not matches_prefix
        if not request.user.is_authenticated and requires_auth:
            return redirect("{}?next={}".format(reverse("core:index"), request.path))

        return get_response(request)

    return middleware
