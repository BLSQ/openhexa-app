from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from habari.catalog.models import Datasource


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
                "title": "Data elements",  # TODO: translate
                "item_name": "data element",  # TODO: translate
                "page": Paginator(datasource.dhis2dataelement_set.all(), 5).page(1),
                "columns": [
                    "Name",
                    "Code",
                    "Values",
                    "Tags",
                    "Last update",
                ],
                "list_url": "dhis2connector:data_element_list",
                "summary_template": "dhis2connector/partials/data_element_summary_item.html",
            },
            "indicator_summary_params": {
                "title": "Indicators",  # TODO: translate
                "item_name": "indicator",  # TODO: translate
                "page": Paginator(datasource.dhis2indicator_set.all(), 5).page(1),
                "columns": [
                    "Name",
                    "Code",
                    "Type",
                    "Tags",
                    "Last update",
                ],
                "list_url": "dhis2connector:data_element_list",
                "summary_template": "dhis2connector/partials/indicator_summary_item.html",
            },
            "breadcrumbs": breadcrumbs,
        },
    )


def data_element_list(request, datasource_id, page_number=1):
    datasource = get_object_or_404(Datasource, pk=datasource_id)
    paginator = Paginator(datasource.dhis2dataelement_set.all(), 10)
    page = paginator.page(page_number)

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
            "data_elements_paginated_params": {
                "title": "Data elements",  # TODO: translate
                "label": f"{page.start_index()} to {page.end_index()} out of {paginator.count}",  # TODO: translate
                "item_name": "data element",  # TODO: translate
                "page": page,
                "columns": [
                    "Name",
                    "Code",
                    "Values",
                    "Tags",
                    "Last update",
                ],
                "summary_template": "dhis2connector/partials/data_element_summary_item.html",
            },
            "breadcrumbs": breadcrumbs,
        },
    )
