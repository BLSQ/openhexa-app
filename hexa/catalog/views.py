from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from .models import CatalogIndex, CatalogIndexType


def index(request):
    breadcrumbs = [(_("Catalog"), "catalog:index")]
    datasource_indexes = CatalogIndex.objects.filter(
        index_type=CatalogIndexType.DATASOURCE.value
    ).for_user(request.user)

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
    results = CatalogIndex.objects.search(query).for_user(request.user)

    return JsonResponse({"results": [result.to_dict() for result in results]})


def search(request):
    query = request.POST.get("query", "")
    results = CatalogIndex.objects.search(query, limit=100).for_user(request.user)

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
