from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from .models import Datasource


def index(request):
    breadcrumbs = [("Catalog", "catalog:index")]
    datasources = Datasource.objects.all()

    return render(
        request,
        "catalog/index.html",
        {
            "datasources": datasources,
            "breadcrumbs": breadcrumbs,
        },
    )


def datasource_detail(request, datasource_id):
    datasource = get_object_or_404(Datasource, pk=datasource_id)

    breadcrumbs = [
        ("Catalog", "catalog:index"),
        (datasource.display_name, "catalog:datasource_detail", datasource_id),
    ]

    return render(
        request,
        "catalog/datasource_detail.html",
        {
            "datasource": datasource,
            "data_elements_summary_params": {
                "item_name": "Data element",  # TODO: translate
                "item_set": datasource.dhis2dataelement_set,
                "columns": [
                    "Name",
                    "Code",
                    "Values",
                    "Tags",
                    "Last update",
                ],
                "list_url": "dhis2connector:data_element_list",
                "item_summary_template": "dhis2connector/partials/data_element_summary_item.html",
            },
            "indicator_summary_params": {
                "item_name": "Indicator",  # TODO: translate
                "item_set": datasource.dhis2indicator_set,
                "columns": [
                    "Name",
                    "Code",
                    "Type",
                    "Tags",
                    "Last update",
                ],
                "list_url": "dhis2connector:data_element_list",
                "item_summary_template": "dhis2connector/partials/indicator_summary_item.html",
            },
            "breadcrumbs": breadcrumbs,
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
