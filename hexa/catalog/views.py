from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from hexa.core.search import get_search_options
from hexa.core.search import search as do_search

from .datagrids import DatasourceGrid
from .models import Index


def index(request: HttpRequest) -> HttpResponse:
    breadcrumbs = [(_("Catalog"), "catalog:index")]
    datasource_indexes = (
        Index.objects.filter_for_user(request.user)
        .roots()
        .select_related("content_type")
        .prefetch_related("tags")
    )
    datasource_grid = DatasourceGrid(
        datasource_indexes, page=int(request.GET.get("page", "1")), request=request
    )

    return render(
        request,
        "catalog/index.html",
        {
            "datasource_grid": datasource_grid,
            "datasource_indexes": datasource_indexes,
            "breadcrumbs": breadcrumbs,
        },
    )


def quick_search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("query", "")

    results = do_search(request.user, query)

    return JsonResponse({"results": [result.to_dict() for result in results]})


def search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("query", "")

    type_options, datasource_options = get_search_options(request.user, query)
    results = do_search(request.user, query, size=100)

    return render(
        request,
        "catalog/search.html",
        {
            "type_options": type_options,
            "datasource_options": datasource_options,
            "query": query,
            "results": [result.to_dict() for result in results],
            "breadcrumbs": [
                (_("Catalog"), "catalog:index"),
                (_("Search"),),
            ],
        },
    )
