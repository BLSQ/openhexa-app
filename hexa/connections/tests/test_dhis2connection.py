from unittest.mock import patch

import responses

from hexa.connections.dhis2_connection import get_client_by_slug, get_dhis2_metadata
from hexa.connections.tests.fixtures.data_elements import (
    data_element_groups,
    data_elements_by_data_elements_group,
    datasets,
)
from hexa.connections.tests.fixtures.indicators import indicator_groups, indicators
from hexa.connections.tests.fixtures.org_units import (
    org_units,
    org_units_groups,
    org_units_levels,
)
from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Connection,
    ConnectionType,
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class TestDHIS2Methods(TestCase):
    USER_SERENA = None
    USER_ADMIN = None

    @classmethod
    def setUp(cls):
        cls.USER_SERENA = User.objects.create_user(
            "serena@bluesquarehub.com",
            "serena's password",
        )
        cls.USER_JIM = User.objects.create_user("jim@bluesquarehub.com", "jim&password")

        cls.USER_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com", "admin", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.USER_ADMIN, name="Workspace's title"
            )

        WorkspaceMembership.objects.create(
            user=cls.USER_SERENA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_JIM,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.EDITOR,
        )
        connection = Connection.objects.create_if_has_perm(
            cls.USER_JIM,
            cls.WORKSPACE,
            name="DHIS2 connection 1",
            slug="dhis2-connection-1",
            connection_type=ConnectionType.DHIS2,
        )
        connection.set_fields(
            cls.USER_JIM,
            [
                {
                    "code": "url",
                    "value": "http://127.0.0.1:8080",
                    "secret": False,
                },
                {"code": "username", "value": "admin", "secret": False},
                {"code": "password", "value": "district", "secret": True},
            ],
        )
        connection.save()

    @responses.activate
    def test_dhis2_connection_from_slug(self):
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/system/ping",
            status=200,
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/system/info",
            json={"version": "2.35"},
            status=200,
        )
        dhis2 = get_client_by_slug("dhis2-connection-1")
        self.assertIsNotNone(dhis2)
        return dhis2

    @responses.activate
    def test_dhis2_org_units(self):
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/organisationUnits?fields=id%2Cname%2Clevel%2Cpath%2Cgeometry&pageSize=1000",
            json={"organisationUnits": org_units},
            status=200,
        )
        dhis2 = self.test_dhis2_connection_from_slug()
        metadata = get_dhis2_metadata(dhis2, "organisation_units")
        self.assertIsNotNone(metadata)

    @responses.activate
    def test_dhis2_org_units_by_groups(self):
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/organisationUnits?fields=id%2Cname%2Clevel%2Cpath%2Cgeometry&filter=organisationUnitGroups.id%3Ain%3A%5BoDkJh5Ddh7d%5D&pageSize=1000",
            json={"organisationUnits": org_units},
            status=200,
        )
        dhis2 = self.test_dhis2_connection_from_slug()
        metadata = get_dhis2_metadata(
            dhis2,
            "organisation_units",
            filter="organisationUnitGroups.id:in:[oDkJh5Ddh7d]",
        )
        self.assertIsNotNone(metadata)

    @responses.activate
    def test_dhis2_org_unit_groups(self):
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080//api/organisationUnits?fields=id%2Cname%2Clevel%2Cpath%2Cgeometry&filter=organisationUnitGroups.id%3Ain%3A%5BoDkJh5Ddh7d%5D&pageSize=1000",
            json={"organisationUnitGroups": org_units_groups},
            status=200,
        )
        dhis2 = self.test_dhis2_connection_from_slug()
        metadata = get_dhis2_metadata(dhis2, type="organisation_unit_groups")
        self.assertIsNotNone(metadata)

    @responses.activate
    def test_dhis2_org_unit_levels(self):
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/filledOrganisationUnitLevels",
            json={"organisationUnitLevels": org_units_levels},
            status=200,
        )
        dhis2 = self.test_dhis2_connection_from_slug()
        metadata = get_dhis2_metadata(dhis2, "organisation_unit_levels")
        self.assertIsNotNone(metadata)

    @responses.activate
    def test_dhis2_datasets(self):
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/dataSets?fields=id%2Cname%2CdataSetElements%2Cindicators%2CorganisationUnits&pageSize=1000",
            json={"dataSets": datasets},
            status=200,
        )
        dhis2 = self.test_dhis2_connection_from_slug()
        metadata = get_dhis2_metadata(dhis2, "datasets")
        self.assertIsNotNone(metadata)

    @responses.activate
    def test_dhis2_data_elements(self):
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/dataElements?fields=id%2Cname%2CaggregationType%2CzeroIsSignificant&pageSize=1000",
            json={"dataElements": data_elements_by_data_elements_group},
            status=200,
        )
        dhis2 = self.test_dhis2_connection_from_slug()
        metadata = get_dhis2_metadata(dhis2, "data_elements")
        self.assertIsNotNone(metadata)

    @responses.activate
    def test_dhis2_data_elements_by_datasets(self):
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080",
            json={"dataElements": data_elements_by_data_elements_group},
            status=200,
        )
        dhis2 = self.test_dhis2_connection_from_slug()
        metadata = get_dhis2_metadata(
            dhis2, "data_elements", filter="dataSetElements.dataSet.id:in:[lyLU2wR22tC]"
        )
        self.assertIsNotNone(metadata)

    @responses.activate
    def test_dhis2_data_elements_by_groups(self):
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/dataElements",
            json={"dataElements": data_elements_by_data_elements_group},
            status=200,
        )
        dhis2 = self.test_dhis2_connection_from_slug()
        metadata = get_dhis2_metadata(
            dhis2, "data_elements", filter="dataElementGroups.id:in:[oDkJh5Ddh7d]"
        )
        self.assertIsNotNone(metadata)

    @responses.activate
    def test_dhis2_data_element_groups(self):
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/dataElementGroups",
            json={"dataElementGroups": data_element_groups},
            status=200,
        )
        dhis2 = self.test_dhis2_connection_from_slug()
        metadata = get_dhis2_metadata(dhis2, "data_element_groups")
        self.assertIsNotNone(metadata)

    @responses.activate
    def test_dhis2_indicators(self):
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/indicators",
            json={"indicators": indicators},
            status=200,
        )
        dhis2 = self.test_dhis2_connection_from_slug()
        metadata = get_dhis2_metadata(dhis2, "indicator")
        self.assertIsNotNone(metadata)

    @responses.activate
    def test_dhis2_indicators_by_groups(self):
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/indicators",
            json={"indicators": indicators},
            status=200,
        )
        dhis2 = self.test_dhis2_connection_from_slug()
        metadata = get_dhis2_metadata(
            dhis2, "indicator", filter="indicatorGroups.id:in:[PoTnGN0F2n5]"
        )
        self.assertIsNotNone(metadata)

    @responses.activate
    def test_dhis2_indicator_groups(self):
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/indicatorGroups",
            json={"indicatorGroups": indicator_groups},
            status=200,
        )
        dhis2 = self.test_dhis2_connection_from_slug()
        metadata = get_dhis2_metadata(dhis2, "indicator_groups")
        self.assertIsNotNone(metadata)
