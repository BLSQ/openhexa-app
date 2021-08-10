from hexa.plugins.app import ConnectorAppConfig
from django.db.models.signals import post_delete


class ConnectorAirflowConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_airflow"
    label = "connector_airflow"

    verbose_name = "Airflow Connector"

    @property
    def route_prefix(self):
        return "airflow"

    def ready(self):
        from .signals import delete_callback
        from .models import ClusterPermission

        post_delete.connect(
            delete_callback,
            sender=ClusterPermission,
            dispatch_uid="connector_airflow_ClusterPermission_delete",
        )
