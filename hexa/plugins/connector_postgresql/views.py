from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from .datagrids import TableGrid
from .models import Database
from ...catalog.lists import build_summary_list_params


def datasource_detail(request, datasource_id):
    datasource = get_object_or_404(
        Database.objects.filter_for_user(request.user), pk=datasource_id
    )
    table_grid = TableGrid(
        datasource.table_set.all(), per_page=2, page=request.GET.get("page", "1")
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (
            datasource.display_name,
            "connector_postgresql:datasource_detail",
            datasource_id,
        ),
    ]

    return render(
        request,
        "connector_postgresql/datasource_detail.html",
        {
            "datasource": datasource,
            "breadcrumbs": breadcrumbs,
            "table_grid": table_grid,
            "object_list_params": build_summary_list_params(
                datasource.table_set.all(),
                per_page=200,
                title=_("Tables"),
                columns=[
                    _("Name"),
                ],
                item_name=_("table"),
                item_template="connector_postgresql/components/object_list_item.html",
            ),
        },
    )


def datasource_sync(request, datasource_id):
    datasource = get_object_or_404(
        Database.objects.filter_for_user(request.user), pk=datasource_id
    )
    sync_result = datasource.sync(request.user)
    messages.success(request, sync_result)

    return redirect(request.META.get("HTTP_REFERER"))
