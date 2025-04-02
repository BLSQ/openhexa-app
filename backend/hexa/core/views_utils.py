from functools import wraps

from django.conf import settings
from django.http import Http404, HttpRequest
from django.shortcuts import redirect


def redirect_to_new_frontend(request: HttpRequest, *_, **__):
    if settings.NEW_FRONTEND_DOMAIN is not None:
        return redirect(
            request.build_absolute_uri(
                f"{settings.NEW_FRONTEND_DOMAIN}{request.get_full_path()}"
            )
        )
    raise Http404("Page not found")


def disable_cors(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        request._cors_enabled = False
        return view_func(request, *args, **kwargs)

    return _wrapped_view
