from django.apps import AppConfig


class S3ConnectorConfig(AppConfig):
    name = "hexa.plugins.connector_s3"
    label = "connector_s3"

    verbose_name = "S3 Connector"

    @property
    def route_prefix(self):
        return "s3"
