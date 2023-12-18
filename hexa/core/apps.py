from hexa.app import CoreAppConfig


class CoreConfig(CoreAppConfig):
    name = "hexa.core"
    label = "core"

    ANONYMOUS_URLS = [
        "core:login",
        "core:ready",
        "graphql",
    ]
