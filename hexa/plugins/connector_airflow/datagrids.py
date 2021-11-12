from django.utils.translation import gettext_lazy as _

from hexa.ui.datagrid import (
    CountryColumn,
    Datagrid,
    DateColumn,
    LeadingColumn,
    LinkColumn,
    StatusColumn,
    TagColumn,
)


class DAGGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="dag_id",
        secondary_text="description",
        icon="get_icon",
    )
    location = CountryColumn(value="index.countries")
    tags = TagColumn(value="index.tags.all")
    last_run = DateColumn(date="last_run.execution_date", label=_("Last run"))
    last_state = StatusColumn(value="last_run.status", label=_("Last state"))
    view = LinkColumn(text="View")

    def get_icon(self, _) -> str:
        return "ui/icons/terminal.html"
