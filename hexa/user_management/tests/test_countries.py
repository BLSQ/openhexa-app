from hexa.core.test import TestCase
from hexa.user_management.countries import get_who_info
from hexa.user_management.tests import SIMPLIFIED_BFA_EXTENT


class CountriesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_get_who_info(self):
        self.assertEqual(
            {
                "region": {"code": "AFR", "name": "African Region"},
                "default_crs": 1234,
                "simplified_extent": SIMPLIFIED_BFA_EXTENT,
            },
            get_who_info("BFA"),
        )
        self.assertEqual(None, get_who_info("SGS"))
        self.assertEqual(None, get_who_info("LOL"))
