import logging
import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger


def setup_sentry(dsn):
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

    # Inject sentry into logging config. set level to ERROR, we don't really want the rest?
    sentry_logging = LoggingIntegration(level=logging.ERROR, event_level=logging.ERROR)

    sentry_sdk.init(
        dsn=dsn,
        integrations=[DjangoIntegration(), sentry_logging],
        traces_sample_rate=traces_sample_rate,
        traces_sampler=sentry_tracer_sampler,
        send_default_pii=True,
        environment=os.environ.get("SENTRY_ENVIRONMENT"),
    )
