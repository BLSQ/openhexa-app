from hexa.app import ConnectorAppConfig


class ConnectorAirflowConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_airflow"
    label = "connector_airflow"

    verbose_name = "Airflow Connector"

    LAST_ACTIVITIES = (
        "hexa.plugins.connector_airflow.last_activities.get_last_activities"
    )

    @property
    def route_prefix(self):
        return "airflow"
