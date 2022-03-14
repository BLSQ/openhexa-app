from hexa.plugins.app import ConnectorAppConfig


class Dhis2ConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_dhis2"
    label = "connector_dhis2"

    verbose_name = "DHIS2 Connector"

    NOTEBOOKS_CREDENTIALS = [
        "hexa.plugins.connector_dhis2.credentials.notebooks_credentials"
    ]

    PIPELINES_CONFIGURATION = [
        "hexa.plugins.connector_dhis2.credentials.pipelines_credentials"
    ]

    @property
    def route_prefix(self):
        return "dhis2"
