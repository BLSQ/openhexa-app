import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from hexa.core.search import get_search_options
from hexa.core.search import search as do_search

from .datagrids import DatasourceGrid
from .models import Datasource, Index
from .queue import datasource_sync_queue


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


@require_POST
def datasource_sync(
    request: HttpRequest, datasource_contenttype_id: int, datasource_id: uuid.UUID
):
    try:
        datasource_type = ContentType.objects.get_for_id(id=datasource_contenttype_id)
    except ContentType.DoesNotExist:
        raise Http404("No Datasource matches the given query.")
    if not issubclass(datasource_type.model_class(), Datasource):
        raise Http404("No Datasource matches the given query.")
    datasource = get_object_or_404(
        datasource_type.model_class().objects.filter_for_user(request.user),
        pk=datasource_id,
    )

    if settings.EXTERNAL_ASYNC_REFRESH and "synchronous" not in request.GET:
        datasource_sync_queue.enqueue(
            "datasource_sync",
            {
                "contenttype_id": datasource_contenttype_id,
                "object_id": str(datasource.id),
            },
        )
        messages.success(request, _("The datasource will soon be synced"))
    else:
        sync_result = datasource.sync()
        messages.success(request, sync_result)

    return redirect(request.META.get("HTTP_REFERER", datasource.get_absolute_url()))
