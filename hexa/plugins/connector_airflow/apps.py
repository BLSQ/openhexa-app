from django.apps import AppConfig


class ConnectorAirflowConfig(AppConfig):
    name = "hexa.plugins.connector_airflow"
    label = "connector_airflow"

    verbose_name = "Airflow Connector"

    @property
    def route_prefix(self):
        return "airflow"
