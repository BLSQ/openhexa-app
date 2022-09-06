from django.utils.translation import gettext_lazy as _

from hexa.data_collections.datagrid import CollectionColumn
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
        width="25%",
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
        width="30%",
    )
    location = CountryColumn(value="countries")
    collections = CollectionColumn()
    last_run = DateColumn(date="object.last_run.execution_date", label=_("Last run"))
    last_state = StatusColumn(value="object.last_run.status", label=_("Last state"))
    view = LinkColumn(text="View")
