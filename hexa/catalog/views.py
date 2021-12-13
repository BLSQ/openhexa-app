import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

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
    results = Index.objects.filter_for_user(request.user).search(query)[:10]

    return JsonResponse({"results": [result.to_dict() for result in results]})


def search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("query", "")
    results = Index.objects.filter_for_user(request.user).search(query)[:100]

    type_options, datasource_options = [], []
    for ct in ContentType.objects.filter(app_label__startswith="connector_"):
        model = ct.model_class()
        if not model:
            continue

        if issubclass(model, Datasource):
            for obj in model.objects.all():
                datasource_options.append(
                    {
                        "value": obj.id,
                        "label": f"({ct.app_label[10:].capitalize()}) {obj.display_name}",
                        "selected": f"datasource:{obj.id}" in query,
                    }
                )
        if hasattr(
            model, "searchable"
        ):  # TODO: remove (see comment in datasource_index command)
            content_code = f"{ct.app_label[10:]}_{ct.model}"
            type_options.append(
                {
                    "value": f"{content_code}",
                    "label": ct.name,
                    "selected": f"type:{content_code}" in query,
                }
            )

    return render(
        request,
        "catalog/search.html",
        {
            "type_options": type_options,
            "datasource_options": datasource_options,
            "query": query,
            "results": results,
            "breadcrumbs": [
                (_("Catalog"), "catalog:index"),
                (_("Search"),),
            ],
        },
    )


@require_http_methods(["POST"])
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
