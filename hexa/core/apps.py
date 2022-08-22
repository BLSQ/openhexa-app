from hexa.app import CoreAppConfig


class CoreConfig(CoreAppConfig):
    name = "hexa.core"
    label = "core"

    ANONYMOUS_URLS = [
        "core:index",
        "core:ready",
    ]

    NOTEBOOKS_CREDENTIALS = ["hexa.core.credential_hook.custom_credentials"]
