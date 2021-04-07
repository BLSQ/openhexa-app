from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from .models import Bucket


def datasource_detail(request, datasource_id):
    datasource = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=datasource_id
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (datasource.display_name, "connector_s3:datasource_detail", datasource_id),
    ]

    return render(
        request,
        "connector_s3/datasource_detail.html",
        {
            "datasource": datasource,
            "breadcrumbs": breadcrumbs,
        },
    )


def datasource_sync(request, datasource_id):
    datasource = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=datasource_id
    )
    sync_result = datasource.sync()
    messages.success(request, sync_result, extra_tags="green")

    return redirect(request.META.get("HTTP_REFERER"))
