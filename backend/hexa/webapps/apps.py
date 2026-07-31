from corsheaders.signals import check_request_enabled

from hexa.app import CoreAppConfig
from hexa.webapps.utils import is_local_dev_origin, is_preview_host


def _allow_local_dev_cors(sender, request, **kwargs):
    """Enable CORS for a local development origin, but only on a preview URL.

    Why this is needed: when a webapp author develops locally, their page runs
    on http://localhost (or a file:// page, whose Origin is "null") and makes
    cross-origin calls to the webapp's preview host. Those origins are not in
    CORS_ALLOWED_ORIGINS, and the browser's preflight OPTIONS is short-circuited
    by CorsMiddleware *before* our webapp middleware runs — so this signal is the
    only place we can tell CorsMiddleware to answer the preflight and echo the
    header. Scoped to preview hosts only (the ephemeral, secret preview URL);
    real webapp subdomains and custom domains keep the default behaviour.
    """
    return is_preview_host(request.get_host()) and is_local_dev_origin(
        request.META.get("HTTP_ORIGIN", "")
    )


class WebappsConfig(CoreAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hexa.webapps"
    label = "webapps"
    ANONYMOUS_URLS = ["webapps:auth_token", "webapps:dev_js"]

    def ready(self):
        super().ready()
        check_request_enabled.connect(_allow_local_dev_cors)
