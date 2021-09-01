from django.utils.translation import ugettext_lazy as _

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

    external = ExternalSection()
    metadata = OpenHexaMetaDataSection()

    @property
    def generic_description(self):
        return _("DHIS2 Instance")
