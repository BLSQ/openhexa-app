import requests
from django.conf import settings
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST


@require_POST
def accept_tos(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and not request.user.accepted_tos:
        request.user.accepted_tos = True
        request.user.save()

    return redirect(reverse("core:login"))


class LogoutView(BaseLogoutView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        hub_response = requests.get(
            f"{settings.NOTEBOOKS_HUB_URL}/logout",
            cookies={"sessionid": request.session.session_key},
            allow_redirects=False,
        )
        hub_response.raise_for_status()

        return response
