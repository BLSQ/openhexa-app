from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from hexa.dashboards.models import ExternalDashboard, Index
from hexa.ui.datacard import (
    CountryProperty,
    Datacard,
    OwnerProperty,
    Section,
    TagProperty,
    TextProperty,
    URLProperty,
)


class DashboardSection(Section):
    title = "Information"
    url = URLProperty(url="url", editable=True)

    class Meta:
        model = ExternalDashboard


class DashboardMetaDataSection(Section):
    title = "OpenHexa Metadata"
    label = TextProperty(text="label", editable=True)
    description = TextProperty(text="description", markdown=True, editable=True)
    owner = OwnerProperty(url="owner.url", text="owner.name", editable=True)
    tags = TagProperty(value="tags.all", editable=True)
    countries = CountryProperty(value="countries", editable=True)

    class Meta:
        model = Index


class DashboardCard(Datacard):
    title = "generic_title"
    subtitle = "generic_description"
    image_src = "screenshot"
    actions = []

    external = DashboardSection()
    metadata = DashboardMetaDataSection(value="index")

    @property
    def generic_title(self):
        return _("External Dashboard")

    @property
    def generic_description(self):
        return _("Link to interesting dashboard, external of OpenHexa")

    @property
    def screenshot(self):
        return reverse("dashboards:dashboard_image", kwargs={"dashboard_id": self.id})
