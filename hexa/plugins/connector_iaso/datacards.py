from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from hexa.catalog.datacards import OpenHexaMetaDataSection
from hexa.ui.datacard import (
    Action,
    Datacard,
    DateProperty,
    JSONProperty,
    Section,
    TextProperty,
)
from hexa.ui.datacard.properties import Property
from hexa.ui.utils import StaticText


class IASOSection(Section):
    title = "IASO Account"

    name = TextProperty(text="name")
    content = TextProperty(text="content_summary")
    url = TextProperty(text="api_url", translate=False)


class IASOCard(Datacard):
    title = "display_name"
    image_src = "iaso_image_src"
    subtitle = "generic_description"
    actions = [Action(label="Sync", url="sync_url", icon="refresh")]

    external = IASOSection()
    metadata = OpenHexaMetaDataSection(value="index")

    @property
    def generic_description(self):
        return _("IASO Account")

    @property
    def iaso_image_src(self):
        return static("connector_iaso/img/symbol.svg")


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


class IASO_OU_ID_Property(Property):
    def __init__(self, *, ou_id: int, **kwargs):
        super().__init__(**kwargs)
        self.ou_id = ou_id

    @property
    def template(self):
        return "ui/datacard/property_url.html"

    def context(self, model, section, **kwargs):
        ou_id = self.get_value(model, self.ou_id, container=section)
        url_value = reverse(
            "connector_iaso:iasoorgunit_detail",
            kwargs={"iasoaccount_id": model.iaso_account.id, "iaso_id": ou_id},
        )
        text_value = ou_id

        return {"text": text_value, "url": url_value, "external": False}


class OrgUnitSection(Section):

    name = TextProperty(text="name")
    created = DateProperty(
        label="Creation date", date="created", date_format="Y-m-d H:i:s"
    )
    last_updated = DateProperty(
        label="Last updated", date="updated", date_format="Y-m-d H:i:s"
    )
    type_id = TextProperty(text="org_unit_type_id")
    type_name = TextProperty(text="org_unit_type_name")
    parent_id = IASO_OU_ID_Property(ou_id="iaso_parent_id")


class OrgUnitCard(Datacard):
    title = StaticText("IASO OrgUnit details")

    external = OrgUnitSection()

    @property
    def generic_description(self):
        return _("IASO OrgUnit")
