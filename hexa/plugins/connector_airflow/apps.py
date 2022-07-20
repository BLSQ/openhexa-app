from django.apps import AppConfig

from hexa.plugins.app import ConnectorAppConfig


class ConnectorAirflowConfig(AppConfig, ConnectorAppConfig):
    name = "hexa.plugins.connector_airflow"
    label = "connector_airflow"

    verbose_name = "Airflow Connector"

    LAST_ACTIVITIES = (
        "hexa.plugins.connector_airflow.last_activities.get_last_activities"
    )

    @property
    def route_prefix(self):
        return "airflow"
