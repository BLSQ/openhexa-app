from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from hexa.catalog.datacards import OpenHexaMetaDataSection

# from hexa.plugins.connector_gcs.models import Object
from hexa.ui.datacard import Datacard, Section, TextProperty
from hexa.ui.utils import StaticText


class BucketSection(Section):
    title = "GoogleCloudStorage Data"

    name = TextProperty(text="name", translate=False)
    content = TextProperty(text="content_summary")


class BucketCard(Datacard):
    title = StaticText("Bucket details")

    external = BucketSection()
    metadata = OpenHexaMetaDataSection(value="index")

    @property
    def generic_description(self):
        return _("GCS Bucket")

    @property
    def gcs_image_src(self):
        return static("connector_gcs/img/symbol.svg")
