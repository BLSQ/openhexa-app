from hexa.plugins.app import ConnectorAppConfig


class S3ConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_s3"
    label = "connector_s3"

    verbose_name = "S3 Connector"

    @property
    def route_prefix(self):
        return "s3"
