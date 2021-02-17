from django.shortcuts import render, get_object_or_404

from habari.catalog.models import Datasource


def data_element_list(request, datasource_id):
    datasource = get_object_or_404(Datasource, pk=datasource_id)

    breadcrumbs = [
        ("Catalog", "catalog:index"),
        (datasource.display_name, "catalog:datasource_detail", datasource_id),
        ("Data Elements", "foo:bar"),
    ]

    return render(
        request,
        "dhis2connector/data_element_list.html",
        {
            "datasource": datasource,
            "breadcrumbs": breadcrumbs,
        },
    )
