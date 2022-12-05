from django.contrib.auth import views as auth_views
from django.conf import settings
import requests


class LogoutView(auth_views.LogoutView):
    def get(self, request, *args, **kwargs):
        # Log out the user from jupyterhub
        requests.get(
            f"{settings.NOTEBOOKS_URL}/hub/logout",
            cookies=request.COOKIES,
        )
        response = super().get(request, *args, **kwargs)
        response.delete_cookie("jupyterhub-session-id")
        response.delete_cookie("jupyterhub-hub-login")

        return response
