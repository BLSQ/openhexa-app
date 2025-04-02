from hexa.app import ConnectorAppConfig


class S3ConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_s3"
    label = "connector_s3"

    verbose_name = "S3 Connector"

    NOTEBOOKS_CREDENTIALS = [
        "hexa.plugins.connector_s3.credentials.notebooks_credentials"
    ]

    PIPELINES_CREDENTIALS = [
        "hexa.plugins.connector_s3.credentials.pipelines_credentials"
    ]

    @property
    def route_prefix(self):
        return "s3"
