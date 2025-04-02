from hexa.app import ConnectorAppConfig


class ConnectorAirflowConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_airflow"
    label = "connector_airflow"

    verbose_name = "Airflow Connector"

    ANONYMOUS_URLS = ["connector_airflow:webhook"]

    @property
    def route_prefix(self):
        return "airflow"
