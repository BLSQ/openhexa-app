from hexa.core.test import TestCase
from hexa.user_management.countries import WHOInfo, get_who_info
from hexa.user_management.tests import SIMPLIFIED_BFA_EXTENT


class CountriesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_get_who_info(self):
        bfa_info = get_who_info("BFA")
        self.assertIsInstance(bfa_info, WHOInfo)
        self.assertEqual({"code": "AFRO", "name": "African Region"}, bfa_info.region)
        self.assertEqual(32630, bfa_info.default_crs)
        self.assertEqual(SIMPLIFIED_BFA_EXTENT, bfa_info.simplified_extent)
        self.assertEqual(None, get_who_info("SGS"))
        self.assertEqual(None, get_who_info("LOL"))
