from django.urls import reverse

from hexa.plugins.connector_gcs.models import Object
from hexa.ui.datagrid import (
    Datagrid,
    DateColumn,
    LeadingColumn,
    LinkColumn,
    TagColumn,
    TextColumn,
)
from hexa.ui.utils import StaticText


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
    last_modified = DateColumn(date="last_modified", date_format="%Y-%m-%d %H:%M:%S %Z")
    link = LinkColumn(text="View")

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
        return "connector_gcs/components/object_grid.html"

    def context(self):
        return {
            **super().context(),
            "refresh_url": reverse(
                "connector_gcs:bucket_refresh", args=[self.parent_model.id]
            ),
            "prefix": self.prefix,
        }
