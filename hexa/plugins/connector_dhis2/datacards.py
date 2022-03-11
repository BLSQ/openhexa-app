from django.contrib.contenttypes.models import ContentType
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from hexa.catalog.datacards import OpenHexaMetaDataSection
from hexa.plugins.connector_dhis2.models import Instance
from hexa.ui.datacard import (
    Action,
    BooleanProperty,
    CodeProperty,
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


class UsageSection(Section):
    title = "Code samples"

    usage_python = CodeProperty(
        label="Usage in Python", code="get_python_usage", language="python"
    )

    def get_python_usage(self, item: Instance):
        return """
%pip install --upgrade git+https://@github.com/blsq/blsq_dqapp.git

from blsq_dqapp.metadata_extraction import Dhis2Client

client = Dhis2Client(
    url=os.environ["{{ instance.env_name }}_URL"],
    username=os.environ["{{ instance.env_name }}_USERNAME"],
    password=os.environ["{{ instance.env_name }}_PASSWORD"],
)
            """.replace(
            "{{ instance.env_name }}", item.env_name
        )


class InstanceCard(Datacard):
    title = "display_name"
    subtitle = "generic_description"
    image_src = "dhis2_image_src"
    actions = [Action(label="Sync", url="get_sync_url", icon="refresh")]

    external = InstanceSection()
    metadata = OpenHexaMetaDataSection(value="index")
    # FIXME: this should be shown only if the user has permission to see the credentials
    usage = UsageSection()

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
    favourite = BooleanProperty(label="Favourite", value="favourite")
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
    favourite = BooleanProperty(label="Favourite", value="favourite")
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
    favourite = BooleanProperty(label="Favourite", value="favourite")
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
