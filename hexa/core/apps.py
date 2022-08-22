from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "hexa.core"
    label = "core"

    NOTEBOOKS_CUSTOM_CREDENTIALS = [
        "hexa.core.credentials.custom_credentials"
    ]
