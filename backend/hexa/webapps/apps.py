from hexa.app import CoreAppConfig


class WebappsConfig(CoreAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hexa.webapps"
    label = "webapps"

    ANONYMOUS_URLS = [
        "webapps:serve-html",
        "webapps:serve-bundle-root",
        "webapps:serve-bundle",
    ]
