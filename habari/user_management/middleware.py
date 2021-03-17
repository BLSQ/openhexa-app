from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from functools import cache


def login_required_middleware(get_response):
    @cache
    def anonymous_urls():
        return [
            reverse("login"),
            reverse("logout"),
            reverse("core:index"),
        ]

    def middleware(request):
        if not request.user.is_authenticated and request.path not in anonymous_urls():
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))

        return get_response(request)

    return middleware
