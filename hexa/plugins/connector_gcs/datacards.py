from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from hexa.catalog.datacards import OpenHexaMetaDataSection
from hexa.data_collections.datacards import CollectionsSection

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


class ObjectSection(Section):
    title = StaticText("GCS Data")

    name = TextProperty(text="filename", translate=False)
    path = TextProperty(text="full_path", translate=False)
    file_type = TextProperty(label="File type", text="type_display", translate=False)
    file_size = TextProperty(
        label="File size", text="file_size_display", translate=False
    )


class ObjectCard(Datacard):
    title = StaticText("Object details")

    external = ObjectSection()
    collections = CollectionsSection()

    @property
    def generic_description(self):
        return _("GCS Bucket")
