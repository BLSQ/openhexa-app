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
    def __init__(self):
        super().__init__(label="Upload", icon="upload", url="None")

    @property
    def template(self):
        return "connector_s3/components/action_upload.html"

    def context(self, grid: Datagrid):
        return {
            **super().context(grid),
            "read_only": not grid.bucket.writable_by(grid.request.user),
        }


class ObjectGrid(Datagrid):
    title = StaticText("Objects")

    lead = LeadingColumn(
        label="Name",
        text="filename",
        icon="get_table_icon",
        translate=False,
    )
    directory = TextColumn(text="parent_key", translate=False)
    tags = TagColumn(value="index.tags.all")
    size = TextColumn(text="file_size_display", translate=False)
    type = TextColumn(text="type_display")
    link = LinkColumn(text="View")

    upload = UploadAction()

    def __init__(self, queryset, *, bucket: Bucket, prefix: str, **kwargs):
        self.bucket = bucket
        self.prefix = prefix
        super().__init__(queryset, **kwargs)

    def get_table_icon(self, obj: Object):
        if obj.type == "directory":
            return "ui/icons/folder_open.html"
        else:
            return "ui/icons/document_text.html"

    @property
    def template(self):
        return "connector_s3/components/object_grid.html"

    def context(self):
        return {
            **super().context(),
            "refresh_url": reverse(
                "connector_s3:bucket_refresh", args=[self.bucket.id]
            ),
            "upload_url": reverse("connector_s3:object_upload", args=[self.bucket.id]),
            "prefix": self.prefix,
        }
