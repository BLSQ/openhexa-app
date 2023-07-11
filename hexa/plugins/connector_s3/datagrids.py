from django.urls import reverse

from hexa.plugins.connector_s3.models import Object
from hexa.ui.datagrid import (
    Action,
    Datagrid,
    DateColumn,
    LeadingColumn,
    LinkColumn,
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
            "read_only": not grid.request.user.has_perm(
                "connector_s3.write", grid.parent_model
            ),
        }


class ObjectGrid(Datagrid):
    title = StaticText("Objects")

    lead = LeadingColumn(
        label="Name",
        text="filename",
        icon="get_table_icon",
        translate=False,
        width="30%",
    )
    directory = TextColumn(text="parent_key", translate=False)
    size = TextColumn(text="file_size_display", translate=False)
    type = TextColumn(text="type_display")
    last_modified = DateColumn(date="last_modified", date_format="%Y-%m-%d %H:%M:%S %Z")
    link = LinkColumn(text="View")

    upload = UploadAction()

    def __init__(self, queryset, *, prefix: str, **kwargs):
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
                "connector_s3:bucket_refresh", args=[self.parent_model.id]
            ),
            "upload_url": reverse(
                "connector_s3:object_upload", args=[self.parent_model.id]
            ),
            "prefix": self.prefix,
        }
