import responses

from hexa.core.test import TestCase
from hexa.plugins.connector_dhis2.api import (
    DataElementResult,
    DataSetResult,
    Dhis2Client,
    Dhis2Result,
    IndicatorResult,
    IndicatorTypeResult,
    OrganisationUnitResult,
)

from .mock_data import (
    mock_data_elements_response,
    mock_datasets_response,
    mock_indicator_types_response,
    mock_indicators_response,
    mock_orgunits_response,
)


class Dhis2Test(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dhis2_client = Dhis2Client(
            url="https://play.dhis2.org.invalid/demo",
            username="admin",
            password="district",
        )

    @responses.activate
    def test_fetch_data_elements(self):
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/demo/api/dataElements.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_data_elements_response,
            status=200,
        )
        results = list(self.dhis2_client.fetch_data_elements())
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], DataElementResult)

    @responses.activate
    def test_fetch_indicator_types(self):
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/demo/api/indicatorTypes.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_indicator_types_response,
            status=200,
        )
        results = list(self.dhis2_client.fetch_indicator_types())
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], IndicatorTypeResult)

    @responses.activate
    def test_fetch_org_unit(self):
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/demo/api/organisationUnits.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_orgunits_response,
            status=200,
        )
        results = list(self.dhis2_client.fetch_organisation_units())
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], OrganisationUnitResult)

    @responses.activate
    def test_fetch_indicators(self):
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/demo/api/indicators.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_indicators_response,
            status=200,
        )
        results = list(self.dhis2_client.fetch_indicators())
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], IndicatorResult)

    @responses.activate
    def test_fetch_datasets(self):
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/demo/api/dataSets.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_datasets_response,
            status=200,
        )
        results = list(self.dhis2_client.fetch_datasets())
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], DataSetResult)

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

        # missing locale -> fallback to default
        result = FooResult(
            {
                "foo": "bax",
                "translations": [
                    {"property": "FOO", "locale": "en_US", "value": "bar"}
                ],
            }
        )
        self.assertIs(result.get_value("foo", "en"), "bax")

        # locale is none -> select english/derivative by default
        self.assertIs(result.get_value("foo"), "bar")

        # defaults
        result = FooResult({})
        self.assertIs(result.get_value("foo", "it"), "baz")
        self.assertIs(result.get_value("foo"), "baz")

    def test_dhis2_locale_none(self):
        de = DataElementResult(
            {
                "code": "CODECODE",
                "lastUpdated": "2019-08-21T13:08:02.032",
                "id": "IDIDID",
                "href": "https://invalid/api/dataElements/IDIDID",
                "created": "2016-04-27T02:20:28.312",
                "name": "Outcome of illness",
                "shortName": "Outcome ",
                "aggregationType": "NONE",
                "domainType": "TRACKER",
                "displayName": "Outcome of illness",
                "publicAccess": "r-------",
                "description": "The final outcome of the case",
                "displayShortName": "Outcome ",
                "externalAccess": False,
                "periodOffset": 0,
                "valueType": "TEXT",
                "displayDescription": "The final outcome of the case",
                "dimensionItem": "UUU",
                "sharing": {
                    "owner": "XXX",
                    "external": False,
                    "users": {},
                    "userGroups": {},
                    "public": "r-------",
                },
                "displayFormName": "Outcome of illness",
                "zeroIsSignificant": False,
                "favorite": False,
                "optionSetValue": True,
                "dimensionItemType": "DATA_ELEMENT",
                "access": {
                    "read": True,
                    "update": True,
                    "externalize": False,
                    "delete": True,
                    "write": True,
                    "manage": True,
                },
                "optionSet": {"id": "WWW"},
                "categoryCombo": {"id": "TTT"},
                "lastUpdatedBy": {
                    "displayName": "TH",
                    "name": "TH",
                    "id": "XXX",
                    "username": "system",
                },
                "createdBy": {
                    "displayName": "JH",
                    "name": "JH",
                    "id": "XXX",
                    "username": "admin",
                },
                "user": {
                    "displayName": "JH",
                    "name": "JH",
                    "id": "XXX",
                    "username": "admin",
                },
                "favorites": [],
                "dataSetElements": [],
                "translations": [
                    {"property": "SHORT_NAME", "locale": "km", "value": "សា្លប់"},
                    {"property": "FORM_NAME", "locale": "km", "value": "សា្លប់"},
                    {"property": "DESCRIPTION", "locale": "km", "value": "សា្លប់"},
                    {"property": "NAME", "locale": "km", "value": "សា្លប់"},
                ],
                "userGroupAccesses": [],
                "dataElementGroups": [],
                "attributeValues": [],
                "userAccesses": [],
                "legendSets": [],
                "aggregationLevels": [],
            }
        )
        self.assertEqual(de.get_value("name"), "Outcome of illness")
