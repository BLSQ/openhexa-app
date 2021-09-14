from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from hexa.catalog.datacards import OpenHexaMetaDataSection
from hexa.plugins.connector_dhis2.models import Instance
from hexa.ui.datacard import (
    Datacard,
    Section,
    TextProperty,
    URLProperty,
    LocaleProperty,
    DateProperty,
    TagProperty,
    CountryProperty,
    Action,
    BooleanProperty,
)


class ClusterSection(Section):
    title = "Airflow Data"

    name = TextProperty(text="airflow_name")
    url = URLProperty(url="airflow_web_url")


class ClusterCard(Datacard):
    title = "display_name"
    subtitle = "generic_description"
    image_src = "dhis2_image_src"
    actions = [Action(label="Sync", url="get_sync_url", icon="refresh")]

    external = ClusterSection()
    # metadata = OpenHexaMetaDataSection(value="index")

    @property
    def generic_description(self):
        return _("Airflow Cluster")

    @property
    def dhis2_image_src(self):
        return static("connector_airflow/img/symbol.svg")

    def get_sync_url(self, instance: Instance):
        return reverse(
            "connector_dhis2:instance_sync", kwargs={"instance_id": instance.id}
        )
