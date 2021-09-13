from hexa.plugins.connector_s3.models import Object
from hexa.ui.datagrid import (
    Datagrid,
    LeadingColumn,
    TextColumn,
    LinkColumn,
    TagColumn,
)


class ObjectGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="filename",
        icon="get_table_icon",
    )
    directory = TextColumn(text="parent_key")
    tags = TagColumn(value="index.tags.all")
    size = TextColumn(text="file_size_display")
    type = TextColumn(text="type_display")
    link = LinkColumn(text="View")

    def get_table_icon(self, obj: Object):
        if obj.type == "directory":
            return "ui/icons/folder_open.html"
        else:
            return "ui/icons/document_text.html"
