from hexa.ui.datagrid import (
    Datagrid,
    LeadingColumn,
)


class TableGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="name",
        icon="get_table_icon",
    )

    def get_table_icon(self, _):
        return "ui/icons/table.html"
