import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.shortcuts import redirect

from .datagrids import ObjectGrid

from .models import Bucket, Credentials


def datasource_detail(request, datasource_id):
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=datasource_id
    )

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
            "datagrid": datagrid,
        },
    )


def datasource_sync(request, datasource_id):
    datasource = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=datasource_id
    )
    sync_result = datasource.sync(request.user)
    messages.success(request, sync_result)

    return redirect(request.META.get("HTTP_REFERER"))


def object_detail(request, bucket_id, path):
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=bucket_id
    )
    object = get_object_or_404(bucket.object_set.filter(orphan=False), key=path)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (bucket.name, "connector_s3:datasource_detail", bucket_id),
    ]

    acc = []
    for i, part in enumerate(object.key.split("/")):
        acc.append(part)
        path = "/".join(acc)
        if i != len(object.key.split("/")) - 1:
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
            "object": object,
            "breadcrumbs": breadcrumbs,
            "datagrid": datagrid,
        },
    )


def object_download(request, bucket_id, path):
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=bucket_id
    )
    object = get_object_or_404(bucket.object_set.all(), key=path)

    response = bucket.get_boto_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": object.bucket.name, "Key": object.key},
        ExpiresIn=60 * 10,
    )

    return redirect(response)
