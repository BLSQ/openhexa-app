from hexa.ui.datagrid import Datagrid, LeadingColumn, TextColumn


class DatasourceGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        main_text="display_name",
        secondary_text="content_type_name",
        image_src="symbol",
    )
    owner = TextColumn(
        main_text="owner.display_name",
        secondary_text="owner.get_organization_type_display",
    )
    content = TextColumn(text="content")
