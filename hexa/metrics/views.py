import urllib.parse

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone

from .models import HttpMethod, Request


def save_redirect(request: HttpRequest, url: str) -> HttpResponse:
    if settings.SAVE_REQUESTS:
        Request.objects.create(
            user_id=request.user.id,
            request_time=timezone.now(),
            response_status=0,
            url=urllib.parse.unquote(url),
            method=HttpMethod.GET,
            response_content_length=0,
            response_time=timezone.now(),
            user_agent=request.META.get("HTTP_USER_AGENT", "").replace(";", ","),
            user_lang=request.META.get("HTTP_ACCEPT_LANGUAGE", "").replace(";", ","),
            referer=request.META.get("HTTP_REFERER", "").replace(";", ","),
        )
    return redirect(url)
