from django.conf import settings
from google.api_core.exceptions import NotFound

from hexa.files import storage


def generate_upload_url(file):
    return storage.generate_upload_url(
        settings.WORKSPACE_DATASETS_BUCKET,
        file.uri,
        file.content_type,
        raise_if_exists=True,
    )


def generate_download_url(file):
    return storage.generate_download_url(
        settings.WORKSPACE_DATASETS_BUCKET, file.uri, force_attachment=True
    )


def get_blob(file):
    try:
        return storage.get_bucket_object(settings.WORKSPACE_DATASETS_BUCKET, file.uri)
    except NotFound:
        return None
