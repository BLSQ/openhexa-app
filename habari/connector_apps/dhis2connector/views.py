from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from habari.catalog.lists import build_summary_list_params, build_paginated_list_params
from habari.catalog.models import Datasource


def datasource_detail(request, datasource_id):
    datasource = get_object_or_404(Datasource, pk=datasource_id)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (datasource.display_name, "dhis2connector:datasource_detail", datasource_id),
    ]

    return render(
        request,
        "catalog/datasource_detail.html",
        {
            "datasource": datasource,
            "data_elements_list_params": build_summary_list_params(
                datasource.dhis2dataelement_set.all(),
                title=_("Data elements"),
                columns=[
                    _("Name"),
                    _("Code"),
                    _("Values"),
                    _("Tags"),
                    _("Last update"),
                ],
                paginated_list_url="dhis2connector:data_element_list",
                item_name=_("data element"),
                item_template="dhis2connector/partials/data_element_list_item.html",
            ),
            "indicators_list_params": build_summary_list_params(
                datasource.dhis2indicator_set.all(),
                title=_("Indicators"),
                columns=[
                    _("Name"),
                    _("Code"),
                    _("Values"),
                    _("Tags"),
                    _("Last update"),
                ],
                paginated_list_url="dhis2connector:indicator_list",
                item_name=_("indicator"),
                item_template="dhis2connector/partials/indicator_list_item.html",
            ),
            "breadcrumbs": breadcrumbs,
        },
    )


def data_element_list(request, datasource_id):
    datasource = get_object_or_404(Datasource, pk=datasource_id)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (datasource.display_name, "dhis2connector:datasource_detail", datasource_id),
        (_("Data Elements"),),
    ]

    return render(
        request,
        "dhis2connector/data_element_list.html",
        {
            "datasource": datasource,
            "data_elements_list_params": build_paginated_list_params(
                datasource.dhis2dataelement_set.all(),
                title=_("Data elements"),
                page_number=int(request.GET.get("page", "1")),
                columns=[
                    _("Name"),
                    _("Code"),
                    _("Values"),
                    _("Tags"),
                    _("Last update"),
                ],
                item_name=_("data element"),
                item_template="dhis2connector/partials/data_element_list_item.html",
            ),
            "breadcrumbs": breadcrumbs,
        },
    )


def indicator_list(request, datasource_id):
    datasource = get_object_or_404(Datasource, pk=datasource_id)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (datasource.display_name, "dhis2connector:datasource_detail", datasource_id),
        ("Indicators",),
    ]

    return render(
        request,
        "dhis2connector/indicator_list.html",
        {
            "datasource": datasource,
            "indicators_list_params": build_paginated_list_params(
                datasource.dhis2indicator_set.all(),
                title=_("Indicators"),
                page_number=int(request.GET.get("page", "1")),
                columns=[
                    _("Name"),
                    _("Code"),
                    _("Values"),
                    _("Tags"),
                    _("Last update"),
                ],
                item_name=_("indicator"),
                item_template="dhis2connector/partials/indicator_list_item.html",
            ),
            "breadcrumbs": breadcrumbs,
        },
    )
