from django.utils.translation import gettext_lazy as _

from hexa.plugins.connector_airflow.models import DAGRun
from hexa.ui.datagrid import (
    BooleanColumn,
    CountryColumn,
    Datagrid,
    DateColumn,
    DurationColumn,
    LeadingColumn,
    LinkColumn,
    StatusColumn,
    TagColumn,
    TextColumn,
)


class DAGGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="dag_id",
        secondary_text="template",
        icon="get_icon",
        translate=False,
    )
    location = CountryColumn(value="index.countries")
    tags = TagColumn(value="index.tags.all")
    last_run = DateColumn(date="last_run.execution_date", label=_("Last run"))
    last_state = StatusColumn(value="last_run.status", label=_("Last state"))
    view = LinkColumn(text="View")

    def get_icon(self, _) -> str:
        return "ui/icons/terminal.html"


class DAGRunGrid(Datagrid):
    lead = LeadingColumn(
        label="Run",
        text="get_label",
        icon="get_icon",
    )
    favorite = BooleanColumn(value="is_favorite")
    execution_date = DateColumn(date="execution_date", label="Execution date")
    user = TextColumn(text="user.display_name")
    state = StatusColumn(value="status")
    duration = DurationColumn(duration="duration")

    view = LinkColumn(text="View")

    @staticmethod
    def get_label(run: DAGRun) -> str:
        if hasattr(run, "favorite") and getattr(run, "favorite") is not None:
            return getattr(run, "favorite")

        return run.run_id

    @staticmethod
    def is_favorite(run: DAGRun) -> str:
        return hasattr(run, "favorite") and getattr(run, "favorite") is not None

    def get_icon(self, _):
        return "ui/icons/play.html"
