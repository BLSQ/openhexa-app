from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from .models import CatalogIndex, CatalogIndexType
from .search import perform_search


def index(request):
    breadcrumbs = [(_("Catalog"), "catalog:index")]
    datasource_indexes = CatalogIndex.objects.filter(
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


def datasource_sync(request, datasource_id):
    datasource_index = get_object_or_404(
        CatalogIndex, pk=datasource_id, index_type=CatalogIndexType.DATASOURCE
    )

    sync_result = datasource_index.object.sync()
    messages.success(request, sync_result, extra_tags="green")

    return redirect(request.META.get("HTTP_REFERER"))


def quick_search(request):
    results = perform_search(request.GET.get("query", ""))

    return JsonResponse({"results": [result.to_dict() for result in results]})


def search(request):
    query = request.POST.get("query", "")
    results = perform_search(query, limit=100)

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
