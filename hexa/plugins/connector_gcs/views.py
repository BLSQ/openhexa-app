import uuid
from logging import getLogger

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .datacards import BucketCard

# from .datagrids import ObjectGrid
from .models import Bucket

logger = getLogger(__name__)


def datasource_detail(request: HttpRequest, datasource_id: uuid.UUID) -> HttpResponse:
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user),
        pk=datasource_id,
    )

    bucket_card = BucketCard(bucket, request=request)
    if request.method == "POST" and bucket_card.save():
        return redirect(request.META["HTTP_REFERER"])

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (bucket.display_name, "connector_gcs:datasource_detail", datasource_id),
    ]

    #    object_grid = ObjectGrid(
    #        bucket.object_set.prefetch_indexes()
    #        .filter(parent_key="/")
    #        .select_related("bucket"),
    #        parent_model=bucket,
    #        prefix="",
    #        per_page=20,
    #        page=int(request.GET.get("page", "1")),
    #        request=request,
    #    )

    return render(
        request,
        "connector_gcs/bucket_detail.html",
        {
            "datasource": bucket,
            "breadcrumbs": breadcrumbs,
            "bucket_card": bucket_card,
            #            "object_grid": object_grid,
        },
    )
