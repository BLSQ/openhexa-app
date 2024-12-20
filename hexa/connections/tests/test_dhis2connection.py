from unittest.mock import patch

from hexa.connections.dhis2_connection import get_client_by_slug, get_dhis2_metadata
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
                    "value": "https://play.im.dhis2.org/stable-2-41-2",
                    "secret": False,
                },
                {"code": "username", "value": "admin", "secret": False},
                {"code": "password", "value": "district", "secret": True},
            ],
        )
        connection.save()

    def test_dhis2_connection_from_slug(self):
        dhis2 = get_client_by_slug("dhis2-connection-1")
        self.assertIsNotNone(dhis2)

    def test_dhis2_org_units(self):
        dhis2 = get_client_by_slug("dhis2-connection-1")
        metadata = get_dhis2_metadata(dhis2, "organisation_units", "id,name", None)
        print(metadata)

    def test_dhis2_org_unit_groups(self):
        dhis2 = get_client_by_slug("dhis2-connection-1")
        metadata = get_dhis2_metadata(dhis2, type="organisation_unit_groups")
        self.assertIsNotNone(metadata)
        print(metadata)

    def test_dhis2_org_unit_levels(self):
        dhis2 = get_client_by_slug("dhis2-connection-1")
        metadata = get_dhis2_metadata(dhis2, "organisation_unit_levels")
        self.assertIsNotNone(metadata)
        print(metadata)

    def test_dhis2_datasets(self):
        dhis2 = get_client_by_slug("dhis2-connection-1")
        metadata = get_dhis2_metadata(dhis2, "datasets")
        self.assertIsNotNone(metadata)
        print(metadata)

    def test_dhis2_data_elements(self):
        dhis2 = get_client_by_slug("dhis2-connection-1")
        # metadata = get_dhis2_metadata(dhis2, "data_elements", filter="dataElementGroups.id:in:[oDkJh5Ddh7d]")
        metadata = get_dhis2_metadata(
            dhis2, "data_elements", filter="dataSetElements.dataSet.id:in:[lyLU2wR22tC]"
        )
        self.assertIsNotNone(metadata)
        print(metadata)

    def test_dhis2_data_element_groups(self):
        dhis2 = get_client_by_slug("dhis2-connection-1")
        metadata = get_dhis2_metadata(dhis2, "data_element_groups")
        self.assertIsNotNone(metadata)
        print(metadata)

    def test_dhis2_indicators(self):
        dhis2 = get_client_by_slug("dhis2-connection-1")
        metadata = get_dhis2_metadata(dhis2, "indicator")
        self.assertIsNotNone(metadata)
        print(metadata)

    def test_dhis2_indicator_groups(self):
        dhis2 = get_client_by_slug("dhis2-connection-1")
        metadata = get_dhis2_metadata(dhis2, "indicator_groups")
        self.assertIsNotNone(metadata)
        print(metadata)
