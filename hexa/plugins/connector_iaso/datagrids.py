from hexa.ui.datagrid import Datagrid, DateColumn, LeadingColumn, LinkColumn, TextColumn
from hexa.ui.utils import StaticText


class IndexGrid(Datagrid):
    title = StaticText("Type of Objects")


class ObjectGrid(Datagrid):
    title = StaticText("Forms")

    lead = LeadingColumn(
        label="Name",
        text="name",
        translate=False,
    )
    created = DateColumn(date="created", date_format="%Y-%m-%d %H:%M:%S")
    last_modified = DateColumn(date="updated", date_format="%Y-%m-%d %H:%M:%S")
    version_id = TextColumn(text="version_id")
    link = LinkColumn(text="View")

    def __init__(self, queryset, *, prefix: str, **kwargs):
        self.prefix = prefix
        super().__init__(queryset, **kwargs)

    def context(self):
        return {
            **super().context(),
            "prefix": self.prefix,
        }
