from django.utils.translation import gettext_lazy as _
from hexa.plugins.connector_dhis2.models import DataElement, DomainType, Indicator
from hexa.ui.datagrid import (
    Datagrid,
    LeadingColumn,
    TextColumn,
    LinkColumn,
    DateColumn,
    TagColumn,
)


class DagGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="name",
        secondary_text="get_value_type_display",
        icon="get_icon",
    )
    code = TextColumn(text="code")
    # tags = TagColumn(value="index.tags.all")
    last_synced = DateColumn(date="instance.last_synced_at")
    view = LinkColumn(text="View")

    def get_icon(self, data_element: DataElement):

        return "ui/icons/exclamation.html"
