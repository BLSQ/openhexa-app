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

    name = TextProperty(text="name")
    url = URLProperty(url="web_url")


class ClusterCard(Datacard):
    title = "name"
    subtitle = "generic_description"
    image_src = "_image_src"

    external = ClusterSection()
    metadata = OpenHexaMetaDataSection(value="index")

    @property
    def generic_description(self):
        return _("Airflow Cluster")

    @property
    def _image_src(self):
        return static("connector_airflow/img/symbol.svg")
