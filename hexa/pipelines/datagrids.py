from django.utils.translation import gettext_lazy as _

from hexa.pipelines.models import Index
from hexa.ui.datagrid import (
    Datagrid,
    LeadingColumn,
    TextColumn,
    LinkColumn,
    DateColumn,
    TagColumn,
)


class EnvironmentGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="display_name",
        secondary_text="content_type_name",
        image_src="symbol",
        detail_url="get_url",
    )
    owner = TextColumn(
        text="owner.display_name",
        secondary_text="owner.get_organization_type_display",
    )
    content = TextColumn(text="content")
    tags = TagColumn(value="tags.all")
    view = LinkColumn(text="View", url="get_url")

    def get_url(self, index: Index):
        return index.object.get_absolute_url()


class RunGrid(Datagrid):
    lead = LeadingColumn(
        label="Pipeline",
        text="dag.airflow_id",
        icon="get_icon",
    )
    execution_date = DateColumn(date="execution_date", label="Execution date")
    state = TextColumn(text="state")

    view = LinkColumn(text="View")

    def get_icon(self, _):
        return "ui/icons/play.html"
