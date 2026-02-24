from datetime import date
from logging import getLogger

import sentry_sdk
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from hexa.superset.models import SupersetDashboard
from hexa.webapps.models import Webapp

logger = getLogger(__name__)


def view_superset_dashboard(request: HttpRequest, dashboard_id: str) -> HttpResponse:
    dashboard: SupersetDashboard = get_object_or_404(SupersetDashboard, id=dashboard_id)

    webapp = getattr(dashboard, "webapp", None)
    if webapp is not None and not webapp.is_public:
        has_access = (
            request.user.is_authenticated
            and Webapp.objects.filter_for_user(request.user)
            .filter(pk=webapp.pk)
            .exists()
        )
        if not has_access:
            return render(request, "superset/no_access.html", status=403)

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

    is_public_view = (
        webapp is not None and webapp.is_public and not request.user.is_authenticated
    )

    return render(
        request,
        "superset/dashboard.html",
        {
            "dashboard": dashboard,
            "guest_token": guest_token,
            "is_public_view": is_public_view,
        },
    )


LEGACY_ENDPOINT_SUNSET_DATE = date(2026, 3, 31)


def view_superset_dashboard_by_external_id(
    request: HttpRequest, external_id: str
) -> HttpResponse:
    """
    Warning: This endpoint is only implemented to ease the migration from the Vercel app to the new system of embedded dashboard.
    It has to be removed in the future once the app https://vercel.com/bluesquare/superset-dashboards-poc is deleted.
    """
    if date.today() >= LEGACY_ENDPOINT_SUNSET_DATE:
        return HttpResponse(
            "This endpoint has been removed. Please use the new dashboard URL. Contact the OpenHEXA team for more information.",
            status=410,
        )

    logger.warning(
        "view_superset_dashboard_by_external_id is deprecated. Use view_superset_dashboard instead.",
        extra={"request": request, "external_id": external_id},
    )
    try:
        dashboard: SupersetDashboard = SupersetDashboard.objects.get(
            external_id=external_id
        )
    except SupersetDashboard.DoesNotExist:
        sentry_sdk.capture_message(
            "Legacy Superset dashboard not found",
            level="error",
            extras={"request": request, "external_id": external_id},
        )
        return HttpResponse(status=404)

    return render(
        request,
        "superset/deprecated_redirect.html",
        {
            "new_url": dashboard.get_absolute_url(),
            "dashboard": dashboard,
            "sunset_date": LEGACY_ENDPOINT_SUNSET_DATE,
        },
    )
