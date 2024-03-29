from django.conf import settings
from google.api_core.exceptions import NotFound

from hexa.files.api import get_storage


def generate_upload_url(file):
    return get_storage().generate_upload_url(
        settings.WORKSPACE_DATASETS_BUCKET,
        file.uri,
        file.content_type,
        raise_if_exists=True,
    )


def generate_download_url(file):
    return get_storage().generate_download_url(
        settings.WORKSPACE_DATASETS_BUCKET, file.uri, force_attachment=True
    )


def get_blob(file):
    try:
        return get_storage().get_bucket_object(
            settings.WORKSPACE_DATASETS_BUCKET, file.uri
        )
    except NotFound:
        return None
