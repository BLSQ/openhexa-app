import requests
from django.conf import settings
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.http import HttpRequest, HttpResponse


class LogoutView(BaseLogoutView):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        response = super().post(request, *args, **kwargs)
        hub_response = requests.get(
            f"{settings.NOTEBOOKS_HUB_URL}/logout",
            cookies={"sessionid": request.session.session_key},
            allow_redirects=False,
        )
        hub_response.raise_for_status()

        return response
