from django.conf import settings
from django.shortcuts import redirect


def login_required_middleware(get_response):
    def middleware(request):
        if not request.user.is_authenticated and request.path not in (
            settings.LOGIN_URL,
            settings.LOGOUT_URL,
        ):
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))

        return get_response(request)

    return middleware
