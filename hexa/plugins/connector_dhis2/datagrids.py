from django.utils.translation import gettext_lazy as _

from hexa.plugins.connector_dhis2.models import (
    DataElement,
    DomainType,
    OrganisationUnit,
)
from hexa.ui.datagrid import (
    Datagrid,
    DateColumn,
    LeadingColumn,
    LinkColumn,
    TagColumn,
    TextColumn,
)


class DataElementGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="name",
        secondary_text="get_value_type_display",
        icon="get_icon",
        translate=False,
    )
    dhis2_id = TextColumn(text="dhis2_id", label="ID", translate=False)
    code = TextColumn(text="code", translate=False)
    tags = TagColumn(value="index.tags.all")
    last_synced = DateColumn(date="instance.last_synced_at")
    view = LinkColumn(text="View")

    def get_icon(self, data_element: DataElement):
        if data_element.domain_type == DomainType.AGGREGATE:
            return "ui/icons/chart_bar.html"
        elif data_element.domain_type == DomainType.TRACKER:
            return "ui/icons/user_circle.html"

        return "ui/icons/exclamation.html"


class OrganisationUnitGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="name",
        secondary_text=None,
        icon="get_icon",
        translate=False,
    )
    dhis2_id = TextColumn(text="dhis2_id", label="ID", translate=False)
    code = TextColumn(text="code", translate=False)
    tags = TagColumn(value="index.tags.all")
    last_synced = DateColumn(date="instance.last_synced_at")
    view = LinkColumn(text="View")

    def get_icon(self, organisation_unit: OrganisationUnit):
        return "ui/icons/location_marker.html"


class IndicatorGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="name",
        secondary_text="indicator_type.name",
        icon="get_icon",
        translate=False,
    )
    dhis2_id = TextColumn(text="dhis2_id", label="ID", translate=False)
    code = TextColumn(text="code", translate=False)
    tags = TagColumn(value="index.tags.all")
    last_synced = DateColumn(date="instance.last_synced_at")
    view = LinkColumn(text="View")

    def get_icon(self, _):
        return "ui/icons/trending_up.html"


class DatasetGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="name",
        icon="get_icon",
        translate=False,
    )
    dhis2_id = TextColumn(text="dhis2_id", label="ID", translate=False)
    code = TextColumn(text="code", translate=False)
    tags = TextColumn(text="todo_tags", translate=False)
    last_synced = DateColumn(date="instance.last_synced_at", label=_("Last synced"))
    view = LinkColumn(text="View")

    def get_icon(self, _):
        return "ui/icons/collection.html"
