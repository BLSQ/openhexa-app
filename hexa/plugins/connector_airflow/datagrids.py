from django.template.defaultfilters import pluralize
from django.utils.translation import gettext_lazy as _

from hexa.plugins.connector_airflow.models import DAGConfig
from hexa.ui.datagrid import (
    CountryColumn,
    Datagrid,
    DateColumn,
    LeadingColumn,
    LinkColumn,
    TagColumn,
    TextColumn,
)


class DagGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="dag_id",
        secondary_text="description",
        icon="get_icon",
    )
    location = CountryColumn(value="index.countries")
    tags = TagColumn(value="index.tags.all")
    last_run = DateColumn(date="last_run.execution_date", label=_("Last run"))
    last_state = TextColumn(text="last_run.state", label=_("Last state"))
    view = LinkColumn(text="View")

    def get_icon(self, _) -> str:
        return "ui/icons/terminal.html"


class DagConfigGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="name",
        icon="get_icon",
    )

    content = TextColumn(text="get_content")

    def get_icon(self, _) -> str:
        return "ui/icons/cog.html"

    def get_content(self, config: DAGConfig) -> str:
        count = len(config.config_data)

        return (
            ""
            if count == 0
            else _("%(count)d configuration key%(suffix)s")
            % {"count": count, "suffix": pluralize(count)}
        )
