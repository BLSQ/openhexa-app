import os

from .base import *  # noqa: F403, F401

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

ENABLE_SQL_LOGGING = os.environ.get("IS_LOCAL_DEV", "0") == "1"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "hexa.core.middlewares": {
            "level": "WARNING",
            "handlers": ["console"],
        },
    },
}

if ENABLE_SQL_LOGGING:
    LOGGING["loggers"]["django.db.backends"] = {
        "level": "DEBUG",
        "handlers": ["console"],
    }

MIDDLEWARE += ["hexa.core.middlewares.query_count_debug_middleware"]  # noqa: F405
