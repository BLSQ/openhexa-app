import os

from .base import *  # noqa: F403, F401

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.security.DisallowedHost": {
            "level": "CRITICAL",
            "propagate": True,
        },
        "django": {
            "level": "INFO",
            "propagate": True,
        },
        "gunicorn": {
            "level": "INFO",
            "propagate": True,
        },
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


# Filesystem configuration
if os.environ.get("WORKSPACE_STORAGE_LOCATION") is None:
    raise Exception("WORKSPACE_STORAGE_LOCATION is not set")

# Filesystem configuration
WORKSPACE_STORAGE_BACKEND = {
    "engine": "hexa.files.backends.fs.FileSystemStorage",
    "options": {
        "data_dir": "/data",
        "ext_bind_path": os.environ.get("WORKSPACE_STORAGE_LOCATION"),
        "file_permissions_mode": 0o777,
        "directory_permissions_mode": 0o777,
    },
}