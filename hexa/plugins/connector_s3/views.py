from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from .datacards import BucketCard, ObjectCard
from .datagrids import ObjectGrid
from .models import Bucket


def datasource_detail(request, datasource_id):
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=datasource_id
    )
    bucket_card = BucketCard(bucket, request=request)
    if request.method == "POST" and bucket_card.save():
        return redirect(request.META["HTTP_REFERER"])

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (bucket.display_name, "connector_s3:datasource_detail", datasource_id),
    ]

    datagrid = ObjectGrid(
        bucket.object_set.filter(parent_key="/", orphan=False),
        per_page=20,
        page=int(request.GET.get("page", "1")),
    )

    # TODO: discuss
    # Shouldn't we place that on datasource / entry models? Or at least a helper function
    # alternative: sync by index_id? weird but practical
    # alternative2: upload as template tag
    sync_url = reverse(
        "catalog:datasource_sync",
        kwargs={
            "datasource_id": bucket.id,
            "datasource_contenttype": ContentType.objects.get_for_model(Bucket).id,
        },
    )

    return render(
        request,
        "connector_s3/datasource_detail.html",
        {
            "datasource": bucket,
            "sync_url": sync_url,
            "breadcrumbs": breadcrumbs,
            "bucket_card": bucket_card,
            "datagrid": datagrid,
        },
    )


def object_detail(request, bucket_id, path):
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=bucket_id
    )
    s3_object = get_object_or_404(bucket.object_set.filter(orphan=False), key=path)
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
        bucket.object_set.filter(parent_key=path, orphan=False),
        per_page=20,
        page=int(request.GET.get("page", "1")),
    )

    # TODO: duplicated with above block
    sync_url = reverse(
        "catalog:datasource_sync",
        kwargs={
            "datasource_id": bucket.id,
            "datasource_contenttype": ContentType.objects.get_for_model(Bucket).id,
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


# TODO: (for both functions): in api.py
def object_download(request, bucket_id, path):
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=bucket_id
    )
    s3_object = get_object_or_404(bucket.object_set.all(), key=path)

    response = bucket.get_boto_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": s3_object.bucket.name, "Key": s3_object.key},
        ExpiresIn=60 * 10,
    )

    return redirect(response)


def object_upload(request, bucket_id):
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=bucket_id
    )
    object_key = request.GET["object_key"]

    response = bucket.get_boto_client().generate_presigned_url(
        "put_object",
        Params={"Bucket": bucket.name, "Key": object_key},
        ExpiresIn=60 * 10,
    )

    return HttpResponse(response, status=201)
