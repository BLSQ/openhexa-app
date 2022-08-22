from hexa.app import ConnectorAppConfig


class IASOConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_iaso"
    label = "connector_iaso"

    verbose_name = "IASO Connector"

    NOTEBOOKS_CREDENTIALS = [
        "hexa.plugins.connector_iaso.credentials.notebooks_credentials"
    ]

    @property
    def route_prefix(self):
        return "iaso"
