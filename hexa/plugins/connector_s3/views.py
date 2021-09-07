from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
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

    return render(
        request,
        "connector_s3/datasource_detail.html",
        {
            "datasource": bucket,
            "breadcrumbs": breadcrumbs,
            "bucket_card": bucket_card,
            "datagrid": datagrid,
        },
    )


def datasource_sync(request, datasource_id):
    datasource = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=datasource_id
    )
    sync_result = datasource.sync()
    messages.success(request, sync_result)

    return redirect(request.META.get("HTTP_REFERER"))


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
    print(acc)

    datagrid = ObjectGrid(
        bucket.object_set.filter(parent_key=path, orphan=False),
        per_page=20,
        page=int(request.GET.get("page", "1")),
    )

    return render(
        request,
        "connector_s3/object_detail.html",
        {
            "datasource": bucket,
            "object": s3_object,
            "object_card": object_card,
            "breadcrumbs": breadcrumbs,
            "datagrid": datagrid,
        },
    )


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
