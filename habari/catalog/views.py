from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from .connectors import get_connector_app_config
from .models import Datasource


def index(request):
    breadcrumbs = [("Catalog", "catalog:index")]
    datasources = Datasource.objects.all()

    return render(
        request,
        "catalog/index.html",
        {"datasources": datasources, "breadcrumbs": breadcrumbs},
    )


def datasource_detail(request, datasource_id):
    datasource = get_object_or_404(Datasource, pk=datasource_id)
    connector_app_config = get_connector_app_config(datasource.datasource_type)

    breadcrumbs = [
        ("Catalog", "catalog:index"),
        (datasource.display_name, "catalog:datasource_detail", datasource_id),
    ]

    return render(
        request,
        "catalog/datasource_detail.html",
        {
            "datasource": datasource,
            "breadcrumbs": breadcrumbs,
            "connector_template_dir": f"{connector_app_config.label}/",
            "connector_static_dir": f"{connector_app_config.label}/",
        },
    )


def datasource_sync(request, datasource_id):
    datasource = get_object_or_404(Datasource, pk=datasource_id)

    try:
        sync_result = datasource.sync()
        messages.success(request, sync_result, extra_tags="green")
    except Datasource.NoConnector as e:
        messages.error(request, e, extra_tags="red")

    return redirect(request.META.get("HTTP_REFERER"))
