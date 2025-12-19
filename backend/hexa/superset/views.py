from logging import getLogger

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from hexa.superset.models import SupersetDashboard

logger = getLogger(__name__)


def view_superset_dashboard(request: HttpRequest, dashboard_id: str) -> HttpResponse:
    dashboard: SupersetDashboard = get_object_or_404(SupersetDashboard, id=dashboard_id)
    client = dashboard.superset_instance.get_client()
    client.authenticate()

    if request.user.is_authenticated:
        user = {
            "username": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        }
    else:
        user = {
            "username": "guest",
            "first_name": "Guest",
            "last_name": "",
        }

    guest_token = client.get_guest_token(
        user=user,
        resources=[{"type": "dashboard", "id": dashboard.external_id}],
    )

    return render(
        request,
        "superset/dashboard.html",
        {"dashboard": dashboard, "guest_token": guest_token},
    )
