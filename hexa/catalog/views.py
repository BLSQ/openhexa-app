from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from .models import Index
from .datagrids import DatasourceGrid


def index(request):
    breadcrumbs = [(_("Catalog"), "catalog:index")]
    datasource_indexes = (
        Index.objects.filter_for_user(request.user)
        .roots()
        .select_related("content_type")
        .prefetch_related("tags")
    )
    datasource_grid = DatasourceGrid(
        datasource_indexes, page=int(request.GET.get("page", "1"))
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


def quick_search(request):
    query = request.GET.get("query", "")
    results = Index.objects.filter_for_user(request.user).search(query)

    return JsonResponse({"results": [result.to_dict() for result in results]})


def search(request):
    query = request.GET.get("query", "")
    results = Index.objects.filter_for_user(request.user).search(query)[:100]

    return render(
        request,
        "catalog/search.html",
        {
            "query": query,
            "results": results,
            "breadcrumbs": [
                (_("Catalog"), "catalog:index"),
                (_("Search"),),
            ],
        },
    )
