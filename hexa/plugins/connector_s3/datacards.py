from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from hexa.catalog.datacards import OpenHexaMetaDataSection
from hexa.plugins.connector_s3.models import Object
from hexa.ui.datacard import Datacard, Section, TextProperty
from hexa.ui.utils import StaticText


class BucketSection(Section):
    title = "S3 Data"

    name = TextProperty(text="name", translate=False)
    content = TextProperty(text="content_summary")


class BucketCard(Datacard):
    title = StaticText("Bucket details")

    external = BucketSection()
    metadata = OpenHexaMetaDataSection(value="index")

    @property
    def generic_description(self):
        return _("S3 Bucket")

    @property
    def s3_image_src(self):
        return static("connector_s3/img/symbol.svg")


class ObjectSection(Section):
    title = StaticText("S3 Data")

    name = TextProperty(text="filename", translate=False)
    path = TextProperty(text="full_path", translate=False)
    file_type = TextProperty(label="File type", text="type_display", translate=False)
    file_size = TextProperty(
        label="File size", text="file_size_display", translate=False
    )


class ObjectCard(Datacard):
    title = StaticText("Object details")

    external = ObjectSection()

    @property
    def generic_description(self):
        return _("S3 Bucket")

    @property
    def s3_image_src(self):
        return static("connector_s3/img/symbol.svg")

    def get_download_url(self, s3_object: Object):
        return reverse(
            "connector_s3:object_download",
            kwargs={"bucket_id": s3_object.bucket.id, "path": s3_object.key},
        )
