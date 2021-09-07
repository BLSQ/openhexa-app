from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .datacards import DatabaseCard
from .datagrids import TableGrid
from .models import Database
from .queue import database_sync_queue


def datasource_detail(request, datasource_id):
    datasource = get_object_or_404(
        Database.objects.filter_for_user(request.user), pk=datasource_id
    )

    database_card = DatabaseCard(datasource, request=request)
    table_grid = TableGrid(
        datasource.table_set.all(),
        per_page=5,
        paginate=False,
        more_url=reverse(
            "connector_postgresql:table_list", kwargs={"datasource_id": datasource_id}
        ),
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
            "database_card": database_card,
            "table_grid": table_grid,
        },
    )


def table_list(request, datasource_id):
    datasource = get_object_or_404(
        Database.objects.filter_for_user(request.user), pk=datasource_id
    )
    table_grid = TableGrid(
        datasource.table_set.all(), page=int(request.GET.get("page", "1"))
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (
            datasource.display_name,
            "connector_postgresql:datasource_detail",
            datasource_id,
        ),
        (_("Tables"),),
    ]

    return render(
        request,
        "connector_postgresql/table_list.html",
        {
            "datasource": datasource,
            "table_grid": table_grid,
            "breadcrumbs": breadcrumbs,
            "section_title": _(
                "Tables in database %(database)s"
                % {"database": datasource.display_name}
            ),
            "section_label": "%(start)s to %(end)s out of %(total)s"
            % {
                "start": table_grid.start_index,
                "end": table_grid.end_index,
                "total": table_grid.total_count,
            },
        },
    )


def datasource_sync(request, datasource_id):
    datasource = get_object_or_404(
        Database.objects.filter_for_user(request.user), pk=datasource_id
    )

    if settings.DATASOURCE_ASYNC_REFRESH:
        database_sync_queue.enqueue('database_sync', {'database_id': datasource.id})
        messages.success(request, sync_result)
    else:
        sync_result = datasource.sync()
        messages.success(request, _("The datasource will soon be synced"))

    return redirect(request.META.get("HTTP_REFERER"))
