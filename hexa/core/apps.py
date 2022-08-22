from hexa.app import CoreAppConfig


class CoreConfig(CoreAppConfig):
    name = "hexa.core"
    label = "core"

    ANONYMOUS_URLS = [
        "core:index",
        "core:ready",
    ]

    NOTEBOOKS_CUSTOM_CREDENTIALS = ["hexa.core.credentials.custom_credentials"]
