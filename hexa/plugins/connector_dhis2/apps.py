from hexa.plugins.app import ConnectorAppConfig
from django.db.models.signals import post_delete


class Dhis2ConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_dhis2"
    label = "connector_dhis2"

    verbose_name = "DHIS2 Connector"

    @property
    def route_prefix(self):
        return "dhis2"
