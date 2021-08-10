from hexa.plugins.app import ConnectorAppConfig
from django.db.models.signals import post_delete


class Dhis2ConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_dhis2"
    label = "connector_dhis2"

    verbose_name = "DHIS2 Connector"

    @property
    def route_prefix(self):
        return "dhis2"

    def ready(self):
        from .signals import delete_callback
        from .models import InstancePermission

        post_delete.connect(
            delete_callback,
            sender=InstancePermission,
            dispatch_uid="connector_dhis2_InstancePermission_delete",
        )
