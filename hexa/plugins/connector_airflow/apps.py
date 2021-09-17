from hexa.plugins.app import ConnectorAppConfig


class ConnectorAirflowConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_airflow"
    label = "connector_airflow"

    verbose_name = "Airflow Connector"

    @property
    def route_prefix(self):
        return "airflow"
