from hexa.app import CoreAppConfig


class AnalyticsConfig(CoreAppConfig):
    name = "hexa.analytics"
    label = "analytics"

    ANONYMOUS_URLS = ["analytics:track"]
