from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from habari.catalog.models import CatalogIndex, CatalogIndexType


def index(request):
    if request.user.is_authenticated:
        return redirect(reverse("core:dashboard"))

    return render(
        request,
        "core/index.html",
    )


def dashboard(request):
    breadcrumbs = [(_("Dashboard"), "core:dashboard")]

    return render(
        request,
        "core/dashboard.html",
        {
            "counts": {
                "datasources": CatalogIndex.objects.filter(
                    index_type=CatalogIndexType.DATASOURCE
                ).count()
            },
            "breadcrumbs": breadcrumbs,
        },
    )
