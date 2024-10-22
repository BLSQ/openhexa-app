from django.conf import settings

from hexa.files import storage


def generate_upload_url(file_uri, content_type: str, host: str | None = None):
    return storage.generate_upload_url(
        settings.WORKSPACE_DATASETS_BUCKET,
        file_uri,
        content_type=content_type,
        host=host,
        raise_if_exists=True,
    )


def generate_download_url(
    version_file, host: str | None = None, force_attachment: bool = True
):
    return storage.generate_download_url(
        settings.WORKSPACE_DATASETS_BUCKET,
        version_file.uri,
        force_attachment=force_attachment,
        host=host,
    )


def get_blob(uri):
    try:
        return storage.get_bucket_object(settings.WORKSPACE_DATASETS_BUCKET, uri)
    except storage.exceptions.NotFound:
        return None
