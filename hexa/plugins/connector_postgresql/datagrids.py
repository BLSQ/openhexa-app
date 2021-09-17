from django.utils.translation import ugettext_lazy as _

from hexa.plugins.connector_postgresql.models import Table
from hexa.ui.datagrid import Datagrid, LeadingColumn, TagColumn, TextColumn


class TableGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="name",
        icon="get_table_icon",
    )
    tags = TagColumn(value="index.tags.all")
    content = TextColumn(text="get_content")

    def get_table_icon(self, _):
        return "ui/icons/table.html"

    def get_content(self, table: Table):
        return _("%(rows)d rows" % {"rows": table.rows})
