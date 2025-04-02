from typing import Callable

from django.http import HttpRequest, HttpResponse

from hexa.analytics.api import set_user_properties


def set_analytics_middleware(
    get_response: Callable[[HttpRequest], HttpResponse],
) -> Callable[[HttpRequest], HttpResponse]:
    """Send the user properties to the analytics service."""

    def middleware(request: HttpRequest) -> HttpResponse:
        response = get_response(request)
        if getattr(request, "user") and request.user.is_authenticated:
            set_user_properties(request.user)
        return response

    return middleware
