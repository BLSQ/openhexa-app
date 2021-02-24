from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from .models import Datasource


def index(request):
    breadcrumbs = [(_("Catalog"), "catalog:index")]
    datasources = Datasource.objects.all()

    return render(
        request,
        "catalog/index.html",
        {
            "datasources": datasources,
            "breadcrumbs": breadcrumbs,
        },
    )


def datasource_sync(request, datasource_id):
    datasource = get_object_or_404(Datasource, pk=datasource_id)

    try:
        sync_result = datasource.sync()
        messages.success(request, sync_result, extra_tags="green")
    except Datasource.NoConnector as e:
        messages.error(request, e, extra_tags="red")

    return redirect(request.META.get("HTTP_REFERER"))
