import uuid
from logging import getLogger

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect

from .api import generate_download_url, generate_upload_url
from .models import Bucket

logger = getLogger(__name__)


def object_download(
    request: HttpRequest, bucket_id: uuid.UUID, path: str
) -> HttpResponse:
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=bucket_id
    )
    target_object = get_object_or_404(bucket.object_set.all(), key=path)

    if bucket.public:
        download_url = f"https://{bucket.name}.s3.{bucket.region}.amazonaws.com/{target_object.key}"
    else:
        download_url = generate_download_url(
            bucket=bucket,
            target_key=target_object.key,
        )
    return redirect(download_url)


def object_upload(request, bucket_id):
    bucket = get_object_or_404(
        Bucket.objects.filter_for_user(request.user), pk=bucket_id
    )

    if not request.user.has_perm("connector_s3.write", bucket):
        logger.warning("object_upload() called on RO bucket %s", bucket.id)
        raise HttpResponseForbidden(
            "No permission to perform the upload action on this bucket"
        )

    upload_url = generate_upload_url(
        bucket=bucket,
        target_key=request.GET["object_key"],
    )

    return HttpResponse(upload_url, status=201)
