from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from .models import CatalogIndex, CatalogIndexType


def index(request):
    breadcrumbs = [(_("Catalog"), "catalog:index")]
    datasource_indexes = CatalogIndex.objects.filter_for_user(request.user).filter(
        index_type=CatalogIndexType.DATASOURCE.value
    )

    return render(
        request,
        "catalog/index.html",
        {
            "datasource_indexes": datasource_indexes,
            "breadcrumbs": breadcrumbs,
        },
    )


def quick_search(request):
    query = request.GET.get("query", "")
    results = CatalogIndex.objects.filter_for_user(request.user).search(query)

    return JsonResponse({"results": [result.to_dict() for result in results]})


def search(request):
    query = request.POST.get("query", "")
    results = CatalogIndex.objects.filter_for_user(request.user).search(
        query, limit=100
    )

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
