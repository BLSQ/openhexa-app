from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from habari.catalog.models import CatalogIndex, CatalogIndexType


def index(request):
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
