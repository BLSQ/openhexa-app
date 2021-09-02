from hexa.catalog.models import Index
from hexa.ui.datagrid import (
    Datagrid,
    LeadingColumn,
    TextColumn,
    LinkColumn,
    DateColumn,
    CountryColumn,
    TagsColumn,
)


class DatasourceGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="display_name",
        secondary_text="content_type_name",
        image_src="symbol",
        detail_url="get_datasource_url",
    )
    owner = TextColumn(
        text="owner.display_name",
        secondary_text="owner.get_organization_type_display",
    )
    content = TextColumn(text="content")
    tags = TagsColumn()
    location = CountryColumn(countries="countries")
    last_sync = DateColumn(date="last_synced_at", label="Last sync")
    view = LinkColumn(text="View", url="get_datasource_url")

    def get_datasource_url(self, index: Index):
        if not hasattr(index.object, "get_absolute_url") or not callable(
            index.object.get_absolute_url
        ):
            raise NotImplementedError(
                "Datasource models should implement get_absolute_url()"
            )

        return index.object.get_absolute_url()
