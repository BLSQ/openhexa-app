from hexa.app import ConnectorAppConfig


class AccessmodConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_accessmod"
    label = "connector_accessmod"

    verbose_name = "Accessmod Connector"

    ANONYMOUS_URLS = ["connector_accessmod:webhook"]

    @property
    def route_prefix(self):
        return "accessmod"

    def ready(self):
        from . import signals  # noqa
