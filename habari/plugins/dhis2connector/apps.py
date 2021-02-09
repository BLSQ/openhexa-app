from django.utils.translation import gettext_lazy as _

from habari.plugins.app import HabariPluginAppConfig


class Dhis2ConnectorConfig(HabariPluginAppConfig):
    name = "habari.plugins.dhis2connector"
    label = "dhis2connector"

    verbose_name = "DHIS2 Connector"

    @staticmethod
    def get_datasource_types():
        return {"DHIS2": ("DHIS2", _("DHIS2"))}
