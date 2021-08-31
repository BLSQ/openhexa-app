import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.shortcuts import redirect

from hexa.catalog.lists import build_summary_list_params, build_paginated_list_params

from .models import Bucket, Credentials


def datasource_detail(request, datasource_id):
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=datasource_id
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (bucket.display_name, "connector_s3:datasource_detail", datasource_id),
    ]

    return render(
        request,
        "connector_s3/datasource_detail.html",
        {
            "datasource": bucket,
            "breadcrumbs": breadcrumbs,
            "object_list_params": build_summary_list_params(
                bucket.object_set.filter(parent_key="/"),
                title=_("Objects"),
                columns=[
                    _("Name"),
                    _("Size"),
                    _("Type"),
                    _("Last update"),
                ],
                item_name=_("object"),
                item_template="connector_s3/components/object_list_item.html",
            ),
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
    object = get_object_or_404(bucket.object_set.all(), key=path)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (bucket.name, "connector_s3:bucket_detail", bucket_id),
    ]

    acc = []
    for i, part in enumerate(object.key.split("/")):
        acc.append(path)
        if i == 0:
            continue
        breadcrumbs.append(
            (part, "connector_s3:object_detail", bucket_id, "/".join(acc)),
        )

    return render(
        request,
        "connector_s3/object_detail.html",
        {
            "datasource": bucket,
            "object": object,
            "breadcrumbs": breadcrumbs,
            "object_list_params": build_summary_list_params(
                bucket.object_set.filter(parent_key=object.key),
                title=_("Objects"),
                columns=[
                    _("Name"),
                    _("Size"),
                    _("Type"),
                    _("Last update"),
                ],
                item_name=_("object"),
                item_template="connector_s3/components/object_list_item.html",
            ),
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
