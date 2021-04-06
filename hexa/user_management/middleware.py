from django.shortcuts import redirect
from django.urls import reverse
from functools import cache


def login_required_middleware(get_response):
    """Authentication is mandatory for all routes except logout, index and ready endpoint."""

    @cache
    def anonymous_urls():
        return [
            reverse("logout"),
            reverse("core:index"),
            reverse("core:ready"),
            reverse("user:credentials"),
        ]

    def middleware(request):
        if not request.user.is_authenticated and request.path not in anonymous_urls():
            return redirect("%s?next=%s" % (reverse("core:index"), request.path))

        return get_response(request)

    return middleware
