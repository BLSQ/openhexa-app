from django.contrib.contenttypes.models import ContentType
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from hexa.catalog.datacards import OpenHexaMetaDataSection
from hexa.plugins.connector_s3.models import Bucket, Object
from hexa.ui.datacard import Action, CodeProperty, LegacyDatacard, Section, TextProperty


class BucketSection(Section):
    title = "S3 Data"

    name = TextProperty(text="name", translate=False)
    content = TextProperty(text="content_summary")


class UsageSection(Section):
    title = "Code samples"

    usage_python = CodeProperty(
        label="Usage in Python", code="get_python_usage", language="python"
    )
    usage_r = CodeProperty(label="Usage in R", code="get_r_usage", language="r")

    def get_python_usage(self, item: Bucket):
        return """
# Reading and writing to S3 using Pandas
import pandas as pd

df = pd.read_csv("s3://{{ datasource.name }}/path-in-bucket/example.csv")
df.to_csv("s3://{{ datasource.name }}/other-path-in-bucket/result.csv")


# Using S3FS to work directly with S3 resources
import s3fs, json

fs = s3fs.S3FileSystem()
with fs.open("s3://{{ datasource.name }}/path-in-bucket/example.json", "rb") as f:
    print(len(json.load(f)))
            """.replace(
            "{{ datasource.name }}", item.name
        )

    def get_r_usage(self, item: Bucket):
        return """
library(aws.s3)

# Read CSV file
df <- s3read_using(
    FUN = read.csv,
    object = 's3://{{ datasource.name }}/path-in-bucket/example.csv'
)

# Write CSV file
df.out <- head(df)
s3write_using(
    x = df,
    FUN = write.csv,
    object = 's3://{{ datasource.name }}/path-in-bucket/some-output.csv'
)
            """.replace(
            "{{ datasource.name }}", item.name
        )


class BucketCard(LegacyDatacard):
    title = "display_name"
    subtitle = "generic_description"
    image_src = "s3_image_src"
    actions = [Action(label="Sync", url="get_sync_url", icon="refresh")]

    external = BucketSection()
    metadata = OpenHexaMetaDataSection(value="index")
    usage = UsageSection()

    @property
    def generic_description(self):
        return _("S3 Bucket")

    @property
    def s3_image_src(self):
        return static("connector_s3/img/symbol.svg")

    def get_sync_url(self, bucket: Bucket):
        return reverse(
            "catalog:datasource_sync",
            kwargs={
                "datasource_id": bucket.id,
                "datasource_contenttype_id": ContentType.objects.get_for_model(
                    Bucket
                ).id,
            },
        )


class ObjectSection(Section):
    title = "S3 Data"

    name = TextProperty(text="filename", translate=False)
    path = TextProperty(text="full_path", translate=False)
    file_type = TextProperty(label="File type", text="type_display", translate=False)
    file_size = TextProperty(
        label="File size", text="file_size_display", translate=False
    )


class ObjectCard(LegacyDatacard):
    title = "display_name"
    subtitle = "generic_description"
    image_src = "s3_image_src"
    actions = [
        Action(label="Download", url="get_download_url", icon="download", method="get")
    ]

    external = ObjectSection()
    metadata = OpenHexaMetaDataSection(value="index")

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
