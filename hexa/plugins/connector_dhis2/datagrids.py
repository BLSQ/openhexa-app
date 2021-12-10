from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from hexa.core.string import generate_filename
from hexa.plugins.connector_dhis2.models import (
    DataElement,
    DomainType,
    OrganisationUnit,
)
from hexa.ui.datagrid import (
    Action,
    Datagrid,
    DateColumn,
    LeadingColumn,
    LinkColumn,
    TagColumn,
    TextColumn,
)
from hexa.ui.utils import StaticText


class DataElementGrid(Datagrid):
    title = StaticText("Data Elements")

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

    download = Action(label="Download", url="get_download_url", icon="table")

    def __init__(self, queryset, *, export_suffix: str = "", **kwargs):
        self.export_suffix = export_suffix
        super().__init__(queryset, **kwargs)

    def get_icon(self, data_element: DataElement):
        if data_element.domain_type == DomainType.AGGREGATE:
            return "ui/icons/chart_bar.html"
        elif data_element.domain_type == DomainType.TRACKER:
            return "ui/icons/user_circle.html"

        return "ui/icons/exclamation.html"

    def get_download_url(self):
        download_url = reverse(
            "connector_dhis2:data_element_download",
            kwargs={"instance_id": self.parent_model.id},
        )
        filename = generate_filename(
            f"{self.parent_model.display_name}{self.export_suffix}_data_elements.csv"
        ).lower()

        return f"{download_url}?filename={filename}"


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
