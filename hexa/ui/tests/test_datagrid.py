import dataclasses
from unittest.mock import MagicMock, Mock

from django import db, test
from django.utils.translation import ugettext_lazy as _

from hexa.ui.datagrid import (
    Datagrid,
    DatagridOptions,
    LeadingColumn,
    LinkColumn,
    TextColumn,
)


class DatagridTest(test.TestCase):
    def build_simple_datagrid_class(self):
        class BikeDatagrid(Datagrid):
            leading = LeadingColumn(
                image_src="get_datasource_image", text="model", secondary_text="brand"
            )
            category = TextColumn(text="category")
            characteristics = TextColumn(text="suspension", secondary_text="groupset")
            view = LinkColumn(url="get_url", text=_("View"))

        return BikeDatagrid

    def test_column_registration(self):
        datagrid_class = self.build_simple_datagrid_class()

        self.assertIsInstance(datagrid_class._meta, DatagridOptions)
        self.assertEqual(4, len(datagrid_class._meta.columns))

    def test_render(self):
        @dataclasses.dataclass
        class Item:
            model: str
            brand: str
            category: str
            type: str
            groupset: str

        qs = MagicMock()
        item = Mock()
        item.display_name.return_value = "Display name"
        qs.iterator.return_value = iter(
            [
                Item(
                    model="Fluid HT",
                    brand="Norco",
                    category="Trail",
                    type="Hardtail",
                    groupset="Shimano Deore",
                ),
                Item(
                    model="SIR 9",
                    brand="Niner",
                    category="Trail",
                    type="Hardtail",
                    groupset="SRAM Eagle SX",
                ),
            ]
        )

        datagrid = self.build_simple_datagrid_class()(queryset=qs, page=1)
        self.assertGreater(len(str(datagrid)), 0)
