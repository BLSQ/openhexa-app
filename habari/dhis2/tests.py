from django import test

from habari.dhis2 import Dhis2Client
from habari.dhis2.api import Dhis2Item


class Dhis2Test(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dhis2_client = Dhis2Client(
            url="https://play.dhis2.org/demo", username="admin", password="district"
        )

    @test.tag("external")
    def test_fetch_data_elements(self):
        results = self.dhis2_client.fetch_data_elements()

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], Dhis2Item)

    @test.tag("external")
    def test_fetch_indicators(self):
        results = self.dhis2_client.fetch_indicators()

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], Dhis2Item)

    def test_dhis2_item_description(self):
        item = Dhis2Item(
            {
                "translations": [
                    {"property": "DESCRIPTION", "locale": "en", "value": "lol"}
                ]
            }
        )
        self.assertIs(item["description"], "lol")

        item = Dhis2Item(
            {
                "translations": [
                    {"property": "DESCRIPTION", "locale": "fr", "value": "lol"}
                ]
            }
        )
        self.assertIs(item["description"], "lol")

        item = Dhis2Item({"translations": []})
        self.assertIs(item["description"], "")
