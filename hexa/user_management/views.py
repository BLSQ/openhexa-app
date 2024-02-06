import requests
from django.conf import settings
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import get_token
from sentry_sdk import capture_exception


class LogoutView(BaseLogoutView):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            hub_response = requests.get(
                f"{settings.NOTEBOOKS_HUB_URL}/logout",
                cookies={
                    "sessionid": request.session.session_key,
                    "csrftoken": get_token(request),
                },
                allow_redirects=False,
            )
            hub_response.raise_for_status()
        except requests.HTTPError as e:
            capture_exception(e)
        finally:
            return super().post(request, *args, **kwargs)
