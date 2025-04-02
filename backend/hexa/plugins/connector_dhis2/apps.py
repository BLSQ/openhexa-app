from hexa.app import ConnectorAppConfig


class Dhis2ConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_dhis2"
    label = "connector_dhis2"

    verbose_name = "DHIS2 Connector"

    NOTEBOOKS_CREDENTIALS = [
        "hexa.plugins.connector_dhis2.credentials.notebooks_credentials"
    ]

    PIPELINES_CREDENTIALS = [
        "hexa.plugins.connector_dhis2.credentials.pipelines_credentials"
    ]
