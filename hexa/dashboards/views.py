import mimetypes
import uuid

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _

from .datacards import DashboardCard
from .datagrids import DashboardGrid
from .models import ExternalDashboard, Index


def dashboard_index(request: HttpRequest) -> HttpResponse:
    breadcrumbs = [(_("Dashboards"), "catalog:index")]
    datasource_indexes = (
        Index.objects.filter_for_user(request.user)
        .roots()
        .select_related("content_type")
        .prefetch_related("tags")
    )
    datasource_grid = DashboardGrid(
        datasource_indexes, page=int(request.GET.get("page", "1")), request=request
    )

    return render(
        request,
        "dashboards/dashboard_index.html",
        {
            "datasource_grid": datasource_grid,
            "datasource_indexes": datasource_indexes,
            "breadcrumbs": breadcrumbs,
        },
    )


def dashboard_detail(request: HttpRequest, dashboard_id: uuid.UUID) -> HttpResponse:
    dashboard = get_object_or_404(
        ExternalDashboard.objects.prefetch_indexes().filter_for_user(request.user),
        pk=dashboard_id,
    )
    dashboard_card = DashboardCard(dashboard, request=request)
    if request.method == "POST" and dashboard_card.save():
        return redirect(request.META["HTTP_REFERER"])

    breadcrumbs = [
        (_("Dashboards"), "dashboards:dashboard_index"),
        (dashboard.index.external_name, "dashboards:dashboard_detail", dashboard_id),
    ]

    return render(
        request,
        "dashboards/dashboard_detail.html",
        {
            "dashboard": dashboard,
            "breadcrumbs": breadcrumbs,
            "dashboard_card": dashboard_card,
        },
    )


def dashboard_image(request: HttpRequest, dashboard_id: uuid.UUID) -> HttpResponse:
    dashboard = get_object_or_404(
        ExternalDashboard.objects.filter_for_user(request.user),
        pk=dashboard_id,
    )
    return HttpResponse(
        dashboard.picture.file.read(),
        content_type=mimetypes.guess_type(dashboard.picture.name)[0],
    )
