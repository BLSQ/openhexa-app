import dataclasses
import datetime

from django.contrib.auth.models import AnonymousUser
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _

from hexa.core.test import TestCase
from hexa.ui.datagrid import (
    Datagrid,
    DatagridOptions,
    DateColumn,
    LeadingColumn,
    LinkColumn,
    TextColumn,
)


class DatagridTest(TestCase):
    def build_simple_datagrid_class(self):
        class BikeDatagrid(Datagrid):
            leading = LeadingColumn(
                image_src="get_datasource_image", text="model", secondary_text="brand"
            )
            category = TextColumn(text="category")
            characteristics = TextColumn(text="suspension", secondary_text="group_set")
            created_at = DateColumn(date="created_at", date_format="%Y-%m-%d %H:%M")
            launch_in = DateColumn(date="launch_in", date_format="%Y-%m-%d %H:%M")
            view = LinkColumn(url="get_url", text=_("View"))

        return BikeDatagrid

    def test_column_registration(self):
        datagrid_class = self.build_simple_datagrid_class()

        self.assertIsInstance(datagrid_class._meta, DatagridOptions)
        self.assertEqual(6, len(datagrid_class._meta.columns))

    def test_render(self):
        @dataclasses.dataclass
        class Item:
            model: str
            brand: str
            category: str
            type: str
            group_set: str
            created_at: datetime.datetime
            launch_in: datetime.datetime

        created_at = parse_datetime("2022-01-02 03:04")
        launch_in = parse_datetime("2022-02-01 10:00")

        queryset = [
            Item(
                model="Fluid HT",
                brand="Norco",
                category="Trail",
                type="Hardtail",
                group_set="Shimano Deore",
                created_at=created_at,
                launch_in=launch_in,
            ),
            Item(
                model="SIR 9",
                brand="Niner",
                category="Trail",
                type="Hardtail",
                group_set="SRAM Eagle SX",
                created_at=created_at,
                launch_in=launch_in,
            ),
        ]

        datagrid = self.build_simple_datagrid_class()(
            queryset=queryset, page=1, request=self.mock_request(AnonymousUser())
        )
        rendered = str(datagrid)
        self.assertGreater(len(rendered), 0)
        self.assertIn("2022-01-02 03:04", rendered)
