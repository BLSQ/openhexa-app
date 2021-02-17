from django.shortcuts import render, get_object_or_404

from habari.catalog.models import Datasource


def data_element_list(request, datasource_id):
    datasource = get_object_or_404(Datasource, pk=datasource_id)

    breadcrumbs = [
        ("Catalog", "catalog:index"),
        (datasource.display_name, "dhis2connector:datasource_detail", datasource_id),
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


def datasource_detail(request, datasource_id):
    datasource = get_object_or_404(Datasource, pk=datasource_id)

    breadcrumbs = [
        ("Catalog", "catalog:index"),
        (datasource.display_name, "dhis2connector:datasource_detail", datasource_id),
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
