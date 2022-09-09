from django.utils.translation import gettext_lazy as _

from hexa.data_collections.datagrid import CollectionColumn
from hexa.plugins.connector_airflow.models import DAGRun
from hexa.ui.datagrid import (
    CountryColumn,
    Datagrid,
    DateColumn,
    DurationColumn,
    LeadingColumn,
    LinkColumn,
    StatusColumn,
    TextColumn,
)


class DAGGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="dag_id",
        secondary_text="dag.template",
        icon="get_icon",
        translate=False,
    )
    location = CountryColumn(value="index.countries")
    collections = CollectionColumn()
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
    execution_date = DateColumn(
        date="execution_date", label="Execution date", date_format="%Y-%m-%d %H:%M"
    )
    state = StatusColumn(value="status")
    duration = DurationColumn(duration="duration", short_form=True)
    user = TextColumn(text="user.display_name")

    view = LinkColumn(text="View")

    @staticmethod
    def get_label(run: DAGRun) -> str:
        if hasattr(run, "favorite") and getattr(run, "favorite") is not None:
            return getattr(run, "favorite")
        elif run.run_id.startswith("manual"):
            return "Manual"
        elif run.run_id.startswith("scheduled"):
            return "Scheduled"

    @staticmethod
    def is_favorite(run: DAGRun) -> str:
        return hasattr(run, "favorite") and getattr(run, "favorite") is not None

    def get_icon(self, run: DAGRun):
        if hasattr(run, "favorite") and getattr(run, "favorite") is not None:
            return "ui/icons/star.html"
        elif run.run_id.startswith("manual"):
            return "ui/icons/play.html"
        elif run.run_id.startswith("scheduled"):
            return "ui/icons/calendar.html"
