from hexa.ui.datagrid import Datagrid, DateColumn, LeadingColumn, LinkColumn, TextColumn
from hexa.ui.utils import StaticText


class FormGrid(Datagrid):
    title = StaticText("Forms")

    lead = LeadingColumn(
        label="Name",
        text="name",
        translate=False,
        width="25%",
    )
    created = DateColumn(date="created", date_format="%Y-%m-%d %H:%M:%S")
    last_modified = DateColumn(
        label="Updated", date="updated", date_format="%Y-%m-%d %H:%M:%S"
    )
    version_id = TextColumn(label="Version ID", text="version_id")
    link = LinkColumn(text="View")

    def __init__(self, queryset, *, prefix: str = "", **kwargs):
        self.prefix = prefix
        super().__init__(queryset, **kwargs)

    def context(self):
        return {
            **super().context(),
            "prefix": self.prefix,
        }


class OrgUnitGrid(Datagrid):
    title = StaticText("Org Units")

    lead = LeadingColumn(
        label="Name",
        text="name",
        translate=False,
    )
    ou_type_name = TextColumn(label="OrgUnit Type", text="org_unit_type_name")
    created = DateColumn(date="created", date_format="%Y-%m-%d %H:%M:%S")
    link = LinkColumn(text="View")

    def __init__(self, queryset, *, prefix: str = "", **kwargs):
        self.prefix = prefix
        super().__init__(queryset, **kwargs)

    def context(self):
        return {
            **super().context(),
            "prefix": self.prefix,
        }
