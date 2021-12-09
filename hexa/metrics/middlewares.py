from typing import Callable

from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils import timezone

from .models import HttpMethod, Request


def track_request_event(
    get_response: Callable[[HttpRequest], HttpResponse]
) -> Callable[[HttpRequest], HttpResponse]:
    def middleware(request: HttpRequest) -> HttpResponse:
        request_time = timezone.now()
        response = get_response(request)
        response_time = timezone.now()

        if (
            settings.SAVE_REQUESTS
            and request.user.is_authenticated
            and request.method in ("GET", "POST")
            and not request.META.get("PATH_INFO", "").startswith("/admin")
            and not request.META.get("HEXA_DO_NOT_TRACK", "false") == "true"
        ):
            Request.objects.create(
                user_id=request.user.id,
                request_time=request_time,
                response_status=response.status_code,
                url=request.META.get("PATH_INFO", ""),
                query_string=request.META.get("QUERY_STRING", ""),
                method=HttpMethod.POST if request.method == "POST" else HttpMethod.GET,
                response_content_length=len(response.content),
                response_time=response_time,
                user_agent=request.META.get("HTTP_USER_AGENT", "").replace(";", ","),
                user_lang=request.META.get("HTTP_ACCEPT_LANGUAGE", "").replace(
                    ";", ","
                ),
                referer=request.META.get("HTTP_REFERER", "").replace(";", ","),
            )
        return response

    return middleware
