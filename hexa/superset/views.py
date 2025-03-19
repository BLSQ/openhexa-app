from logging import getLogger

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

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


def view_superset_dashboard_by_external_id(
    request: HttpRequest, external_id: str
) -> HttpResponse:
    """
    Warning: This endpoint is only implemented to ease the migration from the Vercel app to the new system of embedded dashboard.
    It has to be removed in the future once the app https://vercel.com/bluesquare/superset-dashboards-poc is deleted.
    """
    logger.error(
        "view_superset_dashboard_by_external_id is deprecated. Use view_superset_dashboard instead.",
        extra={"request": request, "external_id": external_id},
    )

    dashboard: SupersetDashboard = get_object_or_404(
        SupersetDashboard, external_id=external_id
    )
    return redirect(dashboard.get_absolute_url())
