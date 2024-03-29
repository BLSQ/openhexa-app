import uuid

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .datacards import DatabaseCard, TableCard
from .datagrids import TableGrid
from .models import Database


def datasource_detail(request: HttpRequest, datasource_id: uuid.UUID) -> HttpResponse:
    datasource = get_object_or_404(
        Database.objects.prefetch_indexes().filter_for_user(request.user),
        pk=datasource_id,
    )

    database_card = DatabaseCard(datasource, request=request)
    if request.method == "POST" and database_card.save():
        return redirect(request.META["HTTP_REFERER"])

    table_grid = TableGrid(
        datasource.table_set.prefetch_indexes().all(),
        per_page=5,
        paginate=False,
        more_url=reverse(
            "connector_postgresql:table_list", kwargs={"datasource_id": datasource_id}
        ),
        request=request,
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


def table_list(request: HttpRequest, datasource_id: uuid.UUID) -> HttpResponse:
    datasource = get_object_or_404(
        Database.objects.prefetch_indexes().filter_for_user(request.user),
        pk=datasource_id,
    )
    table_grid = TableGrid(
        datasource.table_set.prefetch_indexes(),
        page=int(request.GET.get("page", "1")),
        request=request,
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
            "section_title": _(f"Tables in database {datasource.display_name}"),
            "section_label": f"{table_grid.start_index} to {table_grid.end_index} out of {table_grid.total_count}",
        },
    )


def table_detail(
    request: HttpRequest, datasource_id: uuid.UUID, table_id: uuid.UUID
) -> HttpResponse:
    datasource = get_object_or_404(
        Database.objects.prefetch_indexes().filter_for_user(request.user),
        pk=datasource_id,
    )
    table = get_object_or_404(datasource.table_set.prefetch_indexes(), pk=table_id)
    table_card = TableCard(table, request=request)
    if request.method == "POST" and table_card.save():
        return redirect(request.META["HTTP_REFERER"])

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (
            datasource.display_name,
            "connector_postgresql:datasource_detail",
            datasource_id,
        ),
        (_("Tables"), "connector_postgresql:table_list", datasource_id),
        (table.name,),
    ]

    return render(
        request,
        "connector_postgresql/table_detail.html",
        {
            "datasource": datasource,
            "table": table,
            "table_card": table_card,
            "breadcrumbs": breadcrumbs,
        },
    )
