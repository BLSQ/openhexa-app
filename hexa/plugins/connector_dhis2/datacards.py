from django.contrib.contenttypes.models import ContentType
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from hexa.catalog.datacards import OpenHexaMetaDataSection
from hexa.plugins.connector_dhis2.models import Instance
from hexa.ui.datacard import (
    Action,
    BooleanProperty,
    Datacard,
    DateProperty,
    LocaleProperty,
    Section,
    TextProperty,
    URLProperty,
)


class InstanceSection(Section):
    title = "DHIS2 Data"

    name = TextProperty(text="name", translate=False)
    locale = LocaleProperty(locale="locale")
    url = URLProperty(url="url")


class InstanceCard(Datacard):
    title = "display_name"
    subtitle = "generic_description"
    image_src = "dhis2_image_src"
    actions = [Action(label="Sync", url="get_sync_url", icon="refresh")]

    external = InstanceSection()
    metadata = OpenHexaMetaDataSection(value="index")

    @property
    def generic_description(self):
        return _("DHIS2 Instance")

    @property
    def dhis2_image_src(self):
        return static("connector_dhis2/img/symbol.svg")

    def get_sync_url(self, instance: Instance):
        return reverse(
            "catalog:datasource_sync",
            kwargs={
                "datasource_id": instance.id,
                "datasource_contenttype_id": ContentType.objects.get_for_model(
                    Instance
                ).id,
            },
        )


class DataElementSection(Section):
    title = "DHIS2 Data"

    dhis2_id = TextProperty(label="ID", text="dhis2_id", translate=False)
    name = TextProperty(text="name")
    short_name = TextProperty(label="Short name", text="short_name")
    description = TextProperty(label="Description", text="description")
    code = TextProperty(label="Code", text="code", translate=False)
    domain_type = TextProperty(label="Domain type", text="get_domain_type_display")
    value_type = TextProperty(label="Value type", text="get_value_type_display")
    favorite = BooleanProperty(label="Favorite", value="favorite")
    external_access = BooleanProperty(label="External access", value="external_access")
    created = DateProperty(label="Creation date", date="created")
    last_updated = DateProperty(label="Last updated", date="last_updated")


class DataElementCard(Datacard):
    title = "display_name"
    subtitle = "generic_description"
    image_src = "dhis2_image_src"

    external = DataElementSection()
    metadata = OpenHexaMetaDataSection(value="index")

    @property
    def generic_description(self):
        return _("DHIS2 Data Element")

    @property
    def dhis2_image_src(self):
        return static("connector_dhis2/img/symbol.svg")


class OrganisationUnitSection(Section):
    title = "DHIS2 Organisation Unit"

    dhis2_id = TextProperty(label="ID", text="dhis2_id", translate=False)
    name = TextProperty(text="name")
    short_name = TextProperty(label="Short name", text="short_name")
    description = TextProperty(label="Description", text="description")
    code = TextProperty(label="Code", text="code", translate=False)
    leaf = BooleanProperty(label="Leaf", value="leaf")
    domain_type = TextProperty(label="Domain type", text="get_domain_type_display")
    value_type = TextProperty(label="Value type", text="get_value_type_display")
    favorite = BooleanProperty(label="Favorite", value="favorite")
    external_access = BooleanProperty(label="External access", value="external_access")
    created = DateProperty(label="Creation date", date="created")
    last_updated = DateProperty(label="Last updated", date="last_updated")


class OrganisationUnitCard(Datacard):
    title = "display_name"
    subtitle = "generic_description"
    image_src = "dhis2_image_src"

    external = OrganisationUnitSection()
    metadata = OpenHexaMetaDataSection(value="index")

    @property
    def generic_description(self):
        return _("DHIS2 Organisation Unit")

    @property
    def dhis2_image_src(self):
        return static("connector_dhis2/img/symbol.svg")


class IndicatorSection(Section):
    title = "DHIS2 Indicator"

    dhis2_id = TextProperty(label="ID", text="dhis2_id", translate=False)
    name = TextProperty(text="name")
    short_name = TextProperty(label="Short name", text="short_name")
    description = TextProperty(label="Description", text="description")
    code = TextProperty(label="Code", text="code", translate=False)
    indicator_type = TextProperty(
        label="Indicator type", text="indicator_type.display_name"
    )
    annualized = BooleanProperty(label="Annualized", value="annualized")
    favorite = BooleanProperty(label="Favorite", value="favorite")
    external_access = BooleanProperty(label="External access", value="external_access")
    created = DateProperty(label="Creation date", date="created")
    last_updated = DateProperty(label="Last updated", date="last_updated")


class IndicatorCard(Datacard):
    title = "display_name"
    subtitle = "generic_description"
    image_src = "dhis2_image_src"

    external = IndicatorSection()
    metadata = OpenHexaMetaDataSection(value="index")

    @property
    def generic_description(self):
        return _("DHIS2 Indicator")

    @property
    def dhis2_image_src(self):
        return static("connector_dhis2/img/symbol.svg")


class DatasetSection(Section):
    title = "DHIS2 Dataset"

    dhis2_id = TextProperty(label="ID", text="dhis2_id", translate=False)
    name = TextProperty(text="name")
    short_name = TextProperty(label="Short name", text="short_name")
    description = TextProperty(label="Description", text="description")
    code = TextProperty(label="Code", text="code", translate=False)
    created = DateProperty(label="Creation date", date="created")
    last_updated = DateProperty(label="Last updated", date="last_updated")


class DatasetCard(Datacard):
    title = "display_name"
    subtitle = "generic_description"
    image_src = "dhis2_image_src"

    external = DatasetSection()
    metadata = OpenHexaMetaDataSection(value="index")

    @property
    def generic_description(self):
        return _("DHIS2 Dataset")

    @property
    def dhis2_image_src(self):
        return static("connector_dhis2/img/symbol.svg")
