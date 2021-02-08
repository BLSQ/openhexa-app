from django.shortcuts import render

from habari.catalog.models import Datasource


def index(request):
    breadcrumbs = [("Dashboard", "dashboard:index")]

    return render(
        request,
        "dashboard/index.html",
        {
            "counts": {"datasources": Datasource.objects.count()},
            "breadcrumbs": breadcrumbs,
        },
    )
