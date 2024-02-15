import logging
from functools import cache
from typing import Callable

from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.utils import translation
from django_otp.middleware import OTPMiddleware

from hexa.app import get_hexa_app_configs

from .utils import has_configured_two_factor

logger = logging.getLogger(__name__)


def get_view_name(request):
    # Use resolve to get the resolved URL information
    resolver_match = resolve(request.path_info)

    # Extract view_name and app_name from the resolver_match
    view_name = resolver_match.url_name
    app_name = resolver_match.app_name

    return f"{app_name}:{view_name}" if app_name else view_name


@cache
def get_anonymous_urls():
    anonymous_urls = []

    for app_config in get_hexa_app_configs():
        anonymous_urls += getattr(app_config, "ANONYMOUS_URLS", [])

    return anonymous_urls


@cache
def is_protected_routes(request: HttpRequest) -> bool:
    """
    Is the URL should be behind login screen? Must the user accept the TOS to get this page?
    """
    return get_view_name(request) not in get_anonymous_urls()


def login_required_middleware(
    get_response: Callable[[HttpRequest], HttpResponse],
) -> Callable[[HttpRequest], HttpResponse]:
    """Authentication by cookie is mandatory for all routes except the ones specified in
    the app configs ANONYMOUS_URLS.
    Mostly: logout, index, ready and some API endpoints (that implement their own authentication)
    """

    def middleware(request: HttpRequest) -> HttpResponse:
        if not is_protected_routes(request):
            return get_response(request)

        if not request.user.is_authenticated or (
            has_configured_two_factor(request.user) and not request.user.is_verified()
        ):
            if (
                request.method == "GET"
                or request.META.get("CONTENT_TYPE") != "application/json"
            ):
                return redirect(f"{reverse(settings.LOGIN_URL)}?next={request.path}")
            else:
                return HttpResponse(status=401)

        return get_response(request)

    return middleware


class TwoFactorMiddleware(OTPMiddleware):
    """
    This must be installed after
    :class:`~django.contrib.auth.middleware.AuthenticationMiddleware`.
    """


class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        language = None
        if user.is_authenticated:
            language = user.language
        else:
            language = translation.get_language_from_request(request)

        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

        response = self.get_response(request)

        translation.deactivate()
        return response
