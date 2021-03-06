from hexa.app import ConnectorAppConfig


class GCSConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_gcs"
    label = "connector_gcs"

    verbose_name = "GCS Connector"

    NOTEBOOKS_CREDENTIALS = [
        "hexa.plugins.connector_gcs.credentials.notebooks_credentials"
    ]

    PIPELINES_CREDENTIALS = [
        "hexa.plugins.connector_gcs.credentials.pipelines_credentials"
    ]

    @property
    def route_prefix(self):
        return "gcs"
