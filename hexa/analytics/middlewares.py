from typing import Callable

from django.http import HttpRequest, HttpResponse

from hexa.analytics.api import set_user_properties
from hexa.pipelines.authentication import PipelineRunUser


def set_analytics_middleware(
    get_response: Callable[[HttpRequest], HttpResponse],
) -> Callable[[HttpRequest], HttpResponse]:
    """Send the user properties to the analytics service."""

    def middleware(request: HttpRequest) -> HttpResponse:
        response = get_response(request)
        if getattr(request, "user") and request.user.is_authenticated:
            tracked_user = (
                request.user.pipeline_run.user
                if isinstance(request.user, PipelineRunUser)
                else request.user
            )
            set_user_properties(tracked_user)
        return response

    return middleware
