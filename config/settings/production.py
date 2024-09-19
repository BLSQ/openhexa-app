import logging.config
import os

from .base import *  # noqa: F403, F401

if os.environ.get("STORAGE", "local") == "google-cloud":
    # activate google cloud storage, used for dashboard screenshot, ...
    # user generated content
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_BUCKET_NAME = os.environ.get("STORAGE_BUCKET")
    GS_FILE_OVERWRITE = False
    MEDIA_ROOT = None

SENTRY_DSN = os.environ.get("SENTRY_DSN")

if SENTRY_DSN:
    # if sentry -> we are in production, use fluentd handlers
    # inject sentry into logger config afterward.
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {},
        "handlers": {
            "fluentd": {"level": "INFO", "class": "config.logging.GCPHandler"},
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
                "handlers": ["fluentd"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }

    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger

    # Ignore "Invalid HTTP_HOST header" errors
    # as crawlers/bots hit the production hundreds of times per day
    # with the IP instead of the host
    ignore_logger("django.security.DisallowedHost")

    # Sampling rate
    traces_sample_rate = float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "1.0"))

    # Exclude /ready from sentry
    def sentry_tracer_sampler(sampling_context):
        transaction_context = sampling_context.get("transaction_context")
        if transaction_context is None:
            return 0

        op = transaction_context.get("op")

        if op == "http.server":
            path = sampling_context.get("wsgi_environ", {}).get("PATH_INFO")
            # Monitoring endpoints
            if path.startswith("/ready"):
                return 0

        # Default sample rate for everything else
        return traces_sample_rate

    # inject sentry into logging config. set level to ERROR, we don't really want the rest?
    sentry_logging = LoggingIntegration(level=logging.ERROR, event_level=logging.ERROR)

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), sentry_logging],
        traces_sample_rate=traces_sample_rate,
        traces_sampler=sentry_tracer_sampler,
        send_default_pii=True,
        environment=os.environ.get("SENTRY_ENVIRONMENT"),
    )


PIPELINE_SCHEDULER_SPAWNER = "kubernetes"

# GCP Settings if using GCS as a storage backend ###
# Base64 encoded service account key
# To generate a service account key, follow the instructions here:
# import base64
# import json
# WORKSPACE_STORAGE_BACKEND_GCS_SERVICE_ACCOUNT_KEY = base64.b64encode(json.dumps(service_account_key_content).encode("utf-8"))
WORKSPACE_STORAGE_BACKEND = {
    "engine": "hexa.files.backends.gcp.GoogleCloudStorage",
    "options": {
        "service_account_key": os.environ.get(
            "WORKSPACE_STORAGE_BACKEND_GCS_SERVICE_ACCOUNT_KEY"
        ),
        "region": os.environ.get("WORKSPACE_BUCKET_REGION", "europe-west1"),
        "enable_versioning": True,
    },
}


# Trust the X_FORWARDED_PROTO header from the GCP load balancer so Django is aware it is accessed by https
if "TRUST_FORWARDED_PROTO" in os.environ:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Legacy
ACCESSMOD_BUCKET_NAME = os.environ.get("ACCESSMOD_BUCKET_NAME")
ACCESSMOD_MANAGE_REQUESTS_URL = os.environ.get("ACCESSMOD_MANAGE_REQUESTS_URL")
ACCESSMOD_SET_PASSWORD_URL = os.environ.get("ACCESSMOD_SET_PASSWORD_URL")
