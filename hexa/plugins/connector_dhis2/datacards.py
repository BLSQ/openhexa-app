from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from hexa.ui.datacard import (
    Datacard,
    Section,
    TextProperty,
    URLProperty,
    LocaleProperty,
    DateProperty,
    TagsProperty,
    CountryProperty,
)


class ExternalSection(Section):
    title = "External System Data"

    name = TextProperty(text="name")
    locale = LocaleProperty(locale="locale")
    url = URLProperty(url="url")
    last_synced_at = DateProperty(date="last_synced_at")


class OpenHexaMetaDataSection(Section):
    title = "OpenHexa Metadata"

    label = TextProperty(text="only_index.label")
    tags = TagsProperty(tags="only_index.tags.all")
    location = CountryProperty(countries="countries")
    description = TextProperty(text="only_index.description", markdown=True)


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
