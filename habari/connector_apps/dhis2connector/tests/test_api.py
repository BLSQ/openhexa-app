from django import test

from ..api import (
    Dhis2Client,
    DataElementResult,
    IndicatorTypeResult,
    IndicatorResult,
    Dhis2Result,
)


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
        self.assertIsInstance(results[0], DataElementResult)

    @test.tag("external")
    def test_fetch_indicator_types(self):
        results = self.dhis2_client.fetch_indicator_types()

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], IndicatorTypeResult)

    @test.tag("external")
    def test_fetch_indicators(self):
        results = self.dhis2_client.fetch_indicators()

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], IndicatorResult)

    def test_dhis2_result(self):
        class FooResult(Dhis2Result):
            FIELD_SPECS = {"foo": (str, "baz")}

        # property not in specs
        result = FooResult({})
        with self.assertRaises(ValueError):
            result.get_value("bar")

        # property is not translatable
        result = FooResult({"foo": "bar"})
        self.assertIs(result.get_value("foo", "en"), "bar")
        self.assertIs(result.get_value("foo"), "bar")

        # locale is present
        result = FooResult(
            {"translations": [{"property": "FOO", "locale": "en", "value": "bar"}]}
        )
        self.assertIs(result.get_value("foo", "en"), "bar")
        self.assertIs(result.get_value("foo"), "bar")

        # missing locale
        result = FooResult(
            {"translations": [{"property": "FOO", "locale": "fr", "value": "bar"}]}
        )
        self.assertIs(result.get_value("foo", "en"), "bar")
        self.assertIs(result.get_value("foo"), "bar")

        # defaults
        result = FooResult({})
        self.assertIs(result.get_value("foo", "it"), "baz")
        self.assertIs(result.get_value("foo"), "baz")
