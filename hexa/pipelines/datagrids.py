from django.utils.translation import gettext_lazy as _

from hexa.pipelines.models import Index
from hexa.ui.datagrid import (
    CountryColumn,
    Datagrid,
    DateColumn,
    LeadingColumn,
    LinkColumn,
    StatusColumn,
    TagColumn,
    TextColumn,
)


class EnvironmentGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="display_name",
        secondary_text="content_type_name",
        image_src="symbol",
        detail_url="get_url",
    )
    content = TextColumn(text="content")
    tags = TagColumn(value="tags.all")
    view = LinkColumn(text="View", url="get_url")

    def get_url(self, index: Index):
        return index.object.get_absolute_url()


class PipelineIndexGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="display_name",
        secondary_text="content_type_name",
        image_src="symbol",
    )
    location = CountryColumn(value="countries")
    tags = TagColumn(value="tags.all")
    last_run = DateColumn(date="object.last_run.execution_date", label=_("Last run"))
    last_state = StatusColumn(value="object.last_run.status", label=_("Last state"))
    view = LinkColumn(text="View")
