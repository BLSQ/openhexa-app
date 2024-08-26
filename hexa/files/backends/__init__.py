import os

from django.conf import settings
from django.utils.module_loading import import_string


def get_storage_backend():
    try:
        print(settings.WORKSPACE_STORAGE_BACKEND, flush=True)
        print(os.getenv("DJANGO_SETTINGS_MODULE"), flush=True)
        backend_class = import_string(settings.WORKSPACE_STORAGE_BACKEND["engine"])
        return backend_class(**settings.WORKSPACE_STORAGE_BACKEND.get("options", {}))
    except ImportError as e:
        raise ImportError(
            f"Could not import storage backend '{settings.WORKSPACE_STORAGE_BACKEND['engine']}'."
        ) from e
