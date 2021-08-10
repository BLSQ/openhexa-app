from hexa.plugins.app import ConnectorAppConfig
from django.db.models.signals import post_delete


class S3ConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_s3"
    label = "connector_s3"

    verbose_name = "S3 Connector"

    NOTEBOOKS_CREDENTIALS = [
        "hexa.plugins.connector_s3.credentials.notebooks_credentials"
    ]

    @property
    def route_prefix(self):
        return "s3"

    def ready(self):
        from .signals import delete_callback
        from .models import BucketPermission

        post_delete.connect(
            delete_callback,
            sender=BucketPermission,
            dispatch_uid="connector_s3_BucketPermission_delete",
        )
