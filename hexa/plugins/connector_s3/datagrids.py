from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from hexa.plugins.connector_s3.models import Bucket, Object
from hexa.ui.datagrid import (
    Action,
    Datagrid,
    LeadingColumn,
    LinkColumn,
    TagColumn,
    TextColumn,
)
from hexa.ui.utils import StaticText


class UploadAction(Action):
    def __init__(self, *, sync_url: str, **kwargs):
        self.sync_url = sync_url
        super().__init__(**kwargs)

    def context(self, grid: Datagrid):
        return {
            **super().context(grid),
            "sync_url": self.get_value(None, self.sync_url, container=grid),
        }

    @property
    def template(self):
        return "connector_s3/components/action_upload.html"


class ObjectGrid(Datagrid):
    title = StaticText("Objects")

    lead = LeadingColumn(
        label="Name",
        text="filename",
        icon="get_table_icon",
    )
    directory = TextColumn(text="parent_key", translate=False)
    tags = TagColumn(value="index.tags.all")
    size = TextColumn(text="file_size_display", translate=False)
    type = TextColumn(text="type_display")
    link = LinkColumn(text="View")

    upload = UploadAction(
        label="Upload", icon="upload", url="get_upload_url", sync_url="get_sync_url"
    )

    def __init__(self, queryset, *, bucket: Bucket, **kwargs):
        self.bucket = bucket
        super().__init__(queryset, **kwargs)

    def get_table_icon(self, obj: Object):
        if obj.type == "directory":
            return "ui/icons/folder_open.html"
        else:
            return "ui/icons/document_text.html"

    def get_upload_url(self):
        return reverse("connector_s3:object_upload", args=[self.bucket.id])

    def get_sync_url(self):
        # TODO: discuss
        # Shouldn't we place that on datasource / entry models? Or at least a helper function
        # alternative: sync by index_id? weird but practical
        return reverse(
            "catalog:datasource_sync",
            kwargs={
                "datasource_id": self.bucket.id,
                "datasource_contenttype_id": ContentType.objects.get_for_model(
                    Bucket
                ).id,
            },
        )
