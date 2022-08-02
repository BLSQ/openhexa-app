from django.utils.translation import gettext_lazy as _

from hexa.catalog.datacards import OpenHexaMetaDataSection
from hexa.ui.datacard import Datacard, DateProperty, JSONProperty, Section, TextProperty
from hexa.ui.utils import StaticText


class IASOSection(Section):
    title = "IASO Account"

    name = TextProperty(text="name")
    content = TextProperty(text="content_summary")
    url = TextProperty(text="api_url", translate=False)


class IASOCard(Datacard):
    title = StaticText("IASO details")

    external = IASOSection()
    metadata = OpenHexaMetaDataSection(value="index")

    @property
    def generic_description(self):
        return _("IASO Account")


class FormSection(Section):
    title = StaticText("IASO Form")

    name = TextProperty(text="name")
    form_id = TextProperty(label="ID", text="form_id")
    created = DateProperty(
        label="Creation date", date="created", date_format="Y-m-d H:i:s"
    )
    last_updated = DateProperty(
        label="Last updated", date="updated", date_format="Y-m-d H:i:s"
    )
    version_id = TextProperty(label="Version", text="version_id")
    org_unit_types = JSONProperty(code="org_unit_types", label="Org Unit Types")
    projects = JSONProperty(code="projects")


class FormCard(Datacard):
    title = StaticText("Form details")

    external = FormSection()

    @property
    def generic_description(self):
        return _("IASO Form")
