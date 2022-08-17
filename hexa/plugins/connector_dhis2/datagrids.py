from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from hexa.core.string import generate_filename
from hexa.data_collections.datagrid import CollectionColumn
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


class Dhis2Grid(Datagrid):
    def __init__(self, queryset, *, export_prefix: str = "", **kwargs):
        self.export_prefix = export_prefix
        super().__init__(queryset, **kwargs)

    @property
    def download_url(self):
        raise NotImplementedError

    @property
    def export_suffix(self):
        raise NotImplementedError

    def get_download_url(self):
        download_url = reverse(
            self.download_url,
            kwargs={"instance_id": self.parent_model.id},
        )
        filename = generate_filename(
            f"{self.parent_model.display_name}_{self.export_prefix}_{self.export_suffix}.csv"
        )

        return f"{download_url}?filename={filename}"


class DataElementGrid(Dhis2Grid):
    title = StaticText("Data elements")
    lead = LeadingColumn(
        label="Name",
        text="name",
        secondary_text="get_value_type_display",
        icon="get_icon",
        translate=False,
        width="25%",
    )
    dhis2_id = TextColumn(text="dhis2_id", label="ID", translate=False)
    code = TextColumn(text="code", translate=False)
    collections = CollectionColumn(value="collections.all")
    last_synced = DateColumn(date="instance.last_synced_at")
    view = LinkColumn(text="View")

    download = Action(label="Download all", url="get_download_url", icon="table")

    @property
    def download_url(self):
        return "connector_dhis2:data_element_download"

    @property
    def export_suffix(self):
        return "data_elements"

    def get_icon(self, data_element: DataElement):
        if data_element.domain_type == DomainType.AGGREGATE:
            return "ui/icons/chart_bar.html"
        elif data_element.domain_type == DomainType.TRACKER:
            return "ui/icons/user_circle.html"

        return "ui/icons/exclamation.html"


class OrganisationUnitGrid(Dhis2Grid):
    title = StaticText("Organisation units")
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

    download = Action(label="Download all", url="get_download_url", icon="table")

    @property
    def download_url(self):
        return "connector_dhis2:organisation_unit_download"

    @property
    def export_suffix(self):
        return "organisation_units"

    def get_icon(self, _: OrganisationUnit):
        return "ui/icons/location_marker.html"


class IndicatorGrid(Dhis2Grid):
    title = StaticText("Indicators")
    lead = LeadingColumn(
        label="Name",
        text="name",
        secondary_text="indicator_type.name",
        icon="get_icon",
        translate=False,
        width="25%",
    )
    dhis2_id = TextColumn(text="dhis2_id", label="ID", translate=False)
    code = TextColumn(text="code", translate=False)
    tags = TagColumn(value="index.tags.all")
    last_synced = DateColumn(date="instance.last_synced_at")
    view = LinkColumn(text="View")

    download = Action(label="Download all", url="get_download_url", icon="table")

    @property
    def download_url(self):
        return "connector_dhis2:indicator_download"

    @property
    def export_suffix(self):
        return "indicators"

    def get_icon(self, _):
        return "ui/icons/trending_up.html"


class DatasetGrid(Dhis2Grid):
    title = StaticText("Datasets")

    lead = LeadingColumn(
        label="Name",
        text="name",
        icon="get_icon",
        translate=False,
        width="25%",
    )
    dhis2_id = TextColumn(text="dhis2_id", label="ID", translate=False)
    code = TextColumn(text="code", translate=False)
    tags = TextColumn(text="todo_tags", translate=False)
    last_synced = DateColumn(date="instance.last_synced_at", label=_("Last synced"))
    view = LinkColumn(text="View")

    download = Action(label="Download all", url="get_download_url", icon="table")

    @property
    def download_url(self):
        return "connector_dhis2:dataset_download"

    @property
    def export_suffix(self):
        return "datasets"

    def get_icon(self, _):
        return "ui/icons/collection.html"
