from django.conf import settings

from hexa.files import storage


def generate_upload_url(target_key, content_type: str):
    return storage.generate_upload_url(
        settings.WORKSPACE_DATASETS_BUCKET,
        target_key,
        content_type,
        raise_if_exists=True,
    )


def generate_download_url(target_key):
    return storage.generate_download_url(
        settings.WORKSPACE_DATASETS_BUCKET, target_key, force_attachment=True
    )


def get_blob(object_key):
    try:
        return storage.get_bucket_object(settings.WORKSPACE_DATASETS_BUCKET, object_key)
    except storage.exceptions.NotFound:
        return None
