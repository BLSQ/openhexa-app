from hexa.plugins.app import ConnectorAppConfig


class IASOConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_iaso"
    label = "connector_iaso"

    verbose_name = "IASO Connector"

    @property
    def route_prefix(self):
        return "iaso"
