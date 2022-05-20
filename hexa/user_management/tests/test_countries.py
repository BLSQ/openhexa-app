from hexa.core.test import TestCase
from hexa.user_management.countries import get_simplified_extent, get_who_region
from hexa.user_management.tests import SIMPLIFIED_BFA_EXTENT


class CountriesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_get_who_region(self):
        self.assertEqual(
            {"code": "AFR", "name": "African Region"}, get_who_region("BFA")
        )
        self.assertEqual(None, get_who_region("SGS"))
        self.assertEqual(None, get_who_region("LOL"))

    def test_get_simplified_extent(self):
        self.assertEqual(
            SIMPLIFIED_BFA_EXTENT,
            get_simplified_extent("BFA"),
        )
        self.assertEqual(None, get_simplified_extent("SGS"))
        self.assertEqual(None, get_simplified_extent("LOL"))
