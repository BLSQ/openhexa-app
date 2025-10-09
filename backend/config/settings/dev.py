from .base import *  # noqa: F403, F401

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

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
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "hexa.core.middlewares": {
            "level": "WARNING",
            "handlers": ["console"],
        },
    },
}

MIDDLEWARE += ["hexa.core.middlewares.query_count_debug_middleware"]  # noqa: F405
