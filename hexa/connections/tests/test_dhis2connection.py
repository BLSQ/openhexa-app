from pathlib import Path
from unittest.mock import patch

import responses

from hexa.connections.dhis2_client_helper import (
    get_client_by_slug,
    query_dhis2_metadata,
)
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
        responses._add_from_file(
            Path("hexa", "connections", "tests", "fixtures", "dhis2_init.yaml")
        )
        dhis2 = get_client_by_slug("dhis2-connection-1", self.USER_JIM)
        self.assertIsNotNone(dhis2)

    @responses.activate
    def test_dhis2_org_units(self):
        responses._add_from_file(
            Path("hexa", "connections", "tests", "fixtures", "dhis2_init.yaml")
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/organisationUnits?fields=id%2Cname&pageSize=1000",
            json={"organisationUnits": org_units},
            status=200,
        )
        dhis2 = get_client_by_slug("dhis2-connection-1", self.USER_JIM)
        metadata = query_dhis2_metadata(dhis2, "organisationUnits", fields="id,name")
        self.assertEqual(metadata, org_units)

    @responses.activate
    def test_dhis2_org_units_by_groups(self):
        responses._add_from_file(
            Path("hexa", "connections", "tests", "fixtures", "dhis2_init.yaml")
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/organisationUnits?fields=id%2Cname&filter=organisationUnitGroups.id%3Ain%3A%5BoDkJh5Ddh7d%5D&pageSize=1000",
            json={"organisationUnits": org_units},
            status=200,
        )
        dhis2 = get_client_by_slug("dhis2-connection-1", self.USER_JIM)
        metadata = query_dhis2_metadata(
            dhis2,
            "organisationUnits",
            fields="id,name",
            filter="organisationUnitGroups.id:in:[oDkJh5Ddh7d]",
        )
        self.assertEqual(metadata, org_units)

    @responses.activate
    def test_dhis2_org_unit_groups(self):
        responses._add_from_file(
            Path("hexa", "connections", "tests", "fixtures", "dhis2_init.yaml")
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/organisationUnitGroups?fields=id%2Cname&pageSize=1000",
            json={"organisationUnitGroups": org_units_groups},
            status=200,
        )
        dhis2 = get_client_by_slug("dhis2-connection-1", self.USER_JIM)
        metadata = query_dhis2_metadata(
            dhis2, type="organisationUnitGroups", fields="id,name"
        )
        self.assertEqual(metadata, org_units_groups)

    @responses.activate
    def test_dhis2_org_unit_levels(self):
        responses._add_from_file(
            Path("hexa", "connections", "tests", "fixtures", "dhis2_init.yaml")
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/filledOrganisationUnitLevels",
            json=org_units_levels,
            status=200,
        )
        dhis2 = get_client_by_slug("dhis2-connection-1", self.USER_JIM)
        metadata = query_dhis2_metadata(
            dhis2, "organisationUnitLevels", fields="id,name"
        )
        self.assertEqual(metadata, org_units_levels)

    @responses.activate
    def test_dhis2_datasets(self):
        responses._add_from_file(
            Path("hexa", "connections", "tests", "fixtures", "dhis2_init.yaml")
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/dataSets?fields=id%2Cname&pageSize=1000",
            json={"dataSets": datasets},
            status=200,
        )
        dhis2 = get_client_by_slug("dhis2-connection-1", self.USER_JIM)
        metadata = query_dhis2_metadata(dhis2, "datasets", fields="id,name")
        self.assertEqual(metadata, datasets)

    @responses.activate
    def test_dhis2_data_elements(self):
        responses._add_from_file(
            Path("hexa", "connections", "tests", "fixtures", "dhis2_init.yaml")
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/dataElements?fields=id%2Cname&pageSize=1000",
            json={"dataElements": data_elements_by_data_elements_group},
            status=200,
        )
        dhis2 = get_client_by_slug("dhis2-connection-1", self.USER_JIM)
        metadata = query_dhis2_metadata(dhis2, "dataElements", fields="id,name")
        self.assertEqual(metadata, data_elements_by_data_elements_group)

    @responses.activate
    def test_dhis2_data_elements_by_datasets(self):
        responses._add_from_file(
            Path("hexa", "connections", "tests", "fixtures", "dhis2_init.yaml")
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/dataElements?fields=id%2Cname&filter=dataSetElements.dataSet.id%3Ain%3A%5BlyLU2wR22tC%5D&pageSize=1000",
            json={"dataElements": data_elements_by_data_elements_group},
            status=200,
        )
        dhis2 = get_client_by_slug("dhis2-connection-1", self.USER_JIM)
        metadata = query_dhis2_metadata(
            dhis2,
            "dataElements",
            fields="id,name",
            filter="dataSetElements.dataSet.id:in:[lyLU2wR22tC]",
        )
        self.assertIsNotNone(metadata)

    @responses.activate
    def test_dhis2_data_elements_by_groups(self):
        responses._add_from_file(
            Path("hexa", "connections", "tests", "fixtures", "dhis2_init.yaml")
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/dataElements",
            json={"dataElements": data_elements_by_data_elements_group},
            status=200,
        )
        dhis2 = get_client_by_slug("dhis2-connection-1", self.USER_JIM)
        metadata = query_dhis2_metadata(
            dhis2,
            "dataElements",
            fields="id,name",
            filter="dataElementGroups.id:in:[oDkJh5Ddh7d]",
        )
        self.assertEqual(metadata, data_elements_by_data_elements_group)

    @responses.activate
    def test_dhis2_data_element_groups(self):
        responses._add_from_file(
            Path("hexa", "connections", "tests", "fixtures", "dhis2_init.yaml")
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/dataElementGroups",
            json={"dataElementGroups": data_element_groups},
            status=200,
        )
        dhis2 = get_client_by_slug("dhis2-connection-1", self.USER_JIM)
        metadata = query_dhis2_metadata(dhis2, "dataElementGroups", fields="id,name")
        self.assertEqual(metadata, data_element_groups)

    @responses.activate
    def test_dhis2_indicators(self):
        responses._add_from_file(
            Path("hexa", "connections", "tests", "fixtures", "dhis2_init.yaml")
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/indicators?fields=id%2Cname&pageSize=1000",
            json={"indicators": indicators},
            status=200,
        )
        dhis2 = get_client_by_slug("dhis2-connection-1", self.USER_JIM)
        metadata = query_dhis2_metadata(dhis2, "indicators", fields="id,name")
        self.assertEqual(metadata, indicators)

    @responses.activate
    def test_dhis2_indicators_by_groups(self):
        responses._add_from_file(
            Path("hexa", "connections", "tests", "fixtures", "dhis2_init.yaml")
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/indicators?fields=id%2Cname&filter=indicatorGroups.id%3Ain%3A%5BPoTnGN0F2n5%5D&pageSize=1000",
            json={"indicators": indicators},
            status=200,
        )
        dhis2 = get_client_by_slug("dhis2-connection-1", self.USER_JIM)
        metadata = query_dhis2_metadata(
            dhis2,
            "indicators",
            fields="id,name",
            filter="indicatorGroups.id:in:[PoTnGN0F2n5]",
        )
        self.assertEqual(metadata, indicators)

    @responses.activate
    def test_dhis2_indicator_groups(self):
        responses._add_from_file(
            Path("hexa", "connections", "tests", "fixtures", "dhis2_init.yaml")
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:8080/api/indicatorGroups",
            json={"indicatorGroups": indicator_groups},
            status=200,
        )
        dhis2 = get_client_by_slug("dhis2-connection-1", self.USER_JIM)
        metadata = query_dhis2_metadata(dhis2, "indicatorGroups", fields="id,name")
        self.assertEqual(metadata, indicator_groups)