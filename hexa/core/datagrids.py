from hexa.ui.datagrid import (
    Datagrid,
    DateColumn,
    LeadingColumn,
    LinkColumn,
    StatusColumn,
)


class ActivityGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="description",
        image_src="symbol",
        detail_url="get_datasource_url",
        bold=False,
        mark_safe=True,
        width="40%",
    )
    status = StatusColumn(value="status")
    date = DateColumn(date="occurred_at")
    view = LinkColumn(text="View", url="url")
