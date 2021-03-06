import mimetypes
import uuid

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .datacards import DashboardCard
from .datagrids import DashboardGrid
from .models import ExternalDashboard, Index


def visualization_index(request: HttpRequest) -> HttpResponse:
    breadcrumbs = [(_("Visualizations"), "visualizations:visualization_index")]
    dashboard_indexes = Index.objects.filter_for_user(request.user).roots()
    dashboard_grid = DashboardGrid(
        dashboard_indexes, page=int(request.GET.get("page", "1")), request=request
    )

    return render(
        request,
        "visualizations/visualization_index.html",
        {
            "dashboard_grid": dashboard_grid,
            "dashboard_indexes": dashboard_indexes,
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
        (_("Visualizations"), "visualizations:visualization_index"),
        (dashboard.index.display_name, "visualizations:dashboard_detail", dashboard_id),
    ]

    return render(
        request,
        "visualizations/dashboard_detail.html",
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

    if dashboard.picture == "__OVERRIDE_TEST__":
        # special key to enable this call without doing a filesystem check -- useful in test case
        return HttpResponse("")

    return HttpResponse(
        dashboard.picture.file.read(),
        content_type=mimetypes.guess_type(dashboard.picture.name)[0],
    )
