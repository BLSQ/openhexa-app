import uuid

from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from .api import generate_download_url, generate_upload_url
from .datacards import BucketCard, ObjectCard
from .datagrids import ObjectGrid
from .models import Bucket


def datasource_detail(request: HttpRequest, datasource_id: uuid.UUID) -> HttpResponse:
    bucket = get_object_or_404(
        Bucket.objects.prefetch_indexes().filter_for_user(request.user),
        pk=datasource_id,
    )
    bucket_card = BucketCard(bucket, request=request)
    if request.method == "POST" and bucket_card.save():
        return redirect(request.META["HTTP_REFERER"])

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (bucket.display_name, "connector_s3:datasource_detail", datasource_id),
    ]

    datagrid = ObjectGrid(
        bucket.object_set.prefetch_indexes()
        .filter(parent_key="/", orphan=False)
        .select_related("bucket"),
        bucket=bucket,
        per_page=20,
        page=int(request.GET.get("page", "1")),
        request=request,
    )

    return render(
        request,
        "connector_s3/bucket_detail.html",
        {
            "datasource": bucket,
            "breadcrumbs": breadcrumbs,
            "bucket_card": bucket_card,
            "datagrid": datagrid,
        },
    )


def object_detail(
    request: HttpRequest, bucket_id: uuid.UUID, path: str
) -> HttpResponse:
    bucket = get_object_or_404(
        Bucket.objects.prefetch_indexes().filter_for_user(request.user), pk=bucket_id
    )
    s3_object = get_object_or_404(
        bucket.object_set.prefetch_indexes().filter(orphan=False), key=path
    )
    object_card = ObjectCard(model=s3_object, request=request)
    if request.method == "POST" and object_card.save():
        return redirect(request.META["HTTP_REFERER"])

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (bucket.name, "connector_s3:datasource_detail", bucket_id),
    ]

    acc = []
    for i, part in enumerate(s3_object.key.split("/")):
        acc.append(part)
        path = "/".join(acc)
        if i != len(s3_object.key.split("/")) - 1:
            path += "/"
        breadcrumbs.append(
            (part, "connector_s3:object_detail", bucket_id, path),
        )

    datagrid = ObjectGrid(
        bucket.object_set.prefetch_indexes().filter(parent_key=path, orphan=False),
        bucket=bucket,
        per_page=20,
        page=int(request.GET.get("page", "1")),
        request=request,
    )

    # TODO: duplicated with above block
    sync_url = reverse(
        "catalog:datasource_sync",
        kwargs={
            "datasource_id": bucket.id,
            "datasource_contenttype_id": ContentType.objects.get_for_model(Bucket).id,
        },
    )

    return render(
        request,
        "connector_s3/object_detail.html",
        {
            "datasource": bucket,
            "object": s3_object,
            "sync_url": sync_url,
            "object_card": object_card,
            "breadcrumbs": breadcrumbs,
            "datagrid": datagrid,
        },
    )


def object_download(
    request: HttpRequest, bucket_id: uuid.UUID, path: str
) -> HttpResponse:
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=bucket_id
    )
    target_object = get_object_or_404(bucket.object_set.all(), key=path)

    download_url = generate_download_url(
        principal_credentials=bucket.principal_credentials,
        bucket=bucket,
        target_object=target_object,
    )

    return redirect(download_url)


def object_upload(request, bucket_id):
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=bucket_id
    )
    upload_url = generate_upload_url(
        principal_credentials=bucket.principal_credentials,
        bucket=bucket,
        target_key=request.GET["object_key"],
    )

    return HttpResponse(upload_url, status=201)
