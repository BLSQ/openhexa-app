from hexa.app import CoreAppConfig


class WebappsConfig(CoreAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hexa.webapps"
    label = "webapps"
    ANONYMOUS_URLS = ["webapps:auth_token"]
