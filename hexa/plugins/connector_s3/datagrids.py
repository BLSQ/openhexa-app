from hexa.plugins.connector_s3.models import Object
from hexa.ui.datagrid import Datagrid, LeadingColumn, LinkColumn, TagColumn, TextColumn
from hexa.ui.utils import StaticText


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

    def get_table_icon(self, obj: Object):
        if obj.type == "directory":
            return "ui/icons/folder_open.html"
        else:
            return "ui/icons/document_text.html"
