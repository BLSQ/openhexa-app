from datetime import datetime
from typing import Callable

from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from pytz import UTC

from .models import HttpMethod, WebHit


def save_web_hits(
    get_response: Callable[[HttpRequest], HttpResponse]
) -> Callable[[HttpRequest], HttpResponse]:
    def middleware(request: HttpRequest) -> HttpResponse:
        call_time = datetime.utcnow().replace(tzinfo=UTC)
        response = get_response(request)
        reply_time = datetime.utcnow().replace(tzinfo=UTC)

        if (
            settings.SAVE_WEB_HITS
            and request.user.is_authenticated
            and request.method in ("GET", "POST")
        ):
            WebHit.objects.create(
                user_id=request.user.id,
                call_time=call_time,
                call_status=response.status_code,
                call_name=request.META.get("PATH_INFO", ""),
                method=HttpMethod.POST if request.method == "POST" else HttpMethod.GET,
                reply_size=len(response.content),
                reply_time=reply_time,
                user_agent=request.META.get("HTTP_USER_AGENT", "").replace(";", ","),
                user_lang=request.META.get("HTTP_ACCEPT_LANGUAGE", "").replace(
                    ";", ","
                ),
                referer=request.META.get("HTTP_REFERER", "").replace(";", ","),
            )
        return response

    return middleware
