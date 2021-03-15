from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from habari.catalog.models import CatalogIndex, CatalogIndexType


def index(request):
    breadcrumbs = [(_("Dashboard"), "dashboard:index")]

    return render(
        request,
        "dashboard/index.html",
        {
            "counts": {
                "datasources": CatalogIndex.objects.filter(
                    index_type=CatalogIndexType.DATASOURCE
                ).count()
            },
            "breadcrumbs": breadcrumbs,
        },
    )
