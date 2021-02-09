from habari.connector_apps.app import ConnectorAppConfig


class Dhis2ConnectorConfig(ConnectorAppConfig):
    name = "habari.connector_apps.dhis2connector"
    label = "dhis2connector"

    verbose_name = "DHIS2 Connector"

    @property
    def datasource_type(self):
        return "DHIS2"
