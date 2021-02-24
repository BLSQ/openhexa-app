from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from habari.catalog.models import Datasource


def index(request):
    breadcrumbs = [(_("Dashboard"), "dashboard:index")]

    return render(
        request,
        "dashboard/index.html",
        {
            "counts": {"datasources": Datasource.objects.count()},
            "breadcrumbs": breadcrumbs,
        },
    )
