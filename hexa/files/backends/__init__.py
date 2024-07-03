from django.conf import settings
from django.utils.module_loading import import_string

from .s3 import S3Client

__all__ = ["get_storage_backend", "GCPClient", "S3Client"]


def get_storage_backend():
    try:
        backend_class = import_string(settings.WORKSPACE_STORAGE_BACKEND)
        return backend_class()
    except ImportError as e:
        raise ImportError(
            f"Could not import storage backend '{settings.WORKSPACE_STORAGE_BACKEND}'."
        ) from e
