from hexa.plugins.app import ConnectorAppConfig
from django.db.models.signals import post_delete


class PostgresqlConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_postgresql"
    label = "connector_postgresql"

    verbose_name = "Postgresql Connector"

    NOTEBOOKS_CREDENTIALS = [
        "hexa.plugins.connector_postgresql.credentials.notebooks_credentials"
    ]

    @property
    def route_prefix(self):
        return "postgresql"

    def ready(self):
        from .signals import delete_callback
        from .models import DatabasePermission

        post_delete.connect(
            delete_callback,
            sender=DatabasePermission,
            dispatch_uid="connector_postgresql_DatabasePermission_delete",
        )
