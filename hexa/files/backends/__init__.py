from django.conf import settings
from django.utils.module_loading import import_string


def get_storage_backend():
    try:
        backend_class = import_string(settings.WORKSPACE_STORAGE_BACKEND["engine"])
        return backend_class(**settings.WORKSPACE_STORAGE_BACKEND.get("options", {}))
    except ImportError as e:
        raise ImportError(
            f"Could not import storage backend '{settings.WORKSPACE_STORAGE_BACKEND['engine']}'."
        ) from e
