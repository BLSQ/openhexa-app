from hexa.app import CoreAppConfig


class SupersetConfig(CoreAppConfig):
    name = "hexa.superset"
    label = "superset"

    ANONYMOUS_URLS = ["superset:dashboard"]
