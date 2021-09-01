from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from hexa.plugins.connector_dhis2.models import Instance
from hexa.ui.datacard import Datacard, Section, TextProperty


class ExternalSection(Section):
    title = "External System Data"
    name = TextProperty(text="name")


class OpenHexaMetaDataSection(Section):
    title = "OpenHexa Metadata"
    label = TextProperty(text="only_index.label")


class InstanceCard(Datacard):
    title = "display_name"
    subtitle = "generic_description"
    image_src = "dhis2_image_src"

    external = ExternalSection()
    metadata = OpenHexaMetaDataSection()

    @property
    def generic_description(self):
        return _("DHIS2 Instance")

    @property
    def dhis2_image_src(self):
        return f"{settings.STATIC_URL}connector_dhis2/img/symbol.svg"
