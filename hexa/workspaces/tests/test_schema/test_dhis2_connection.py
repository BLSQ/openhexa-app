from unittest.mock import MagicMock, patch

from openhexa.toolbox.dhis2.api import DHIS2Error

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Connection,
    ConnectionType,
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class ConnectiontTest(GraphQLTestCase):
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

    def test_get_org_units(self):
        self.client.force_login(self.USER_JIM)

        dhis2_mock = MagicMock()
        dhis2_mock.meta.organisation_units.return_value = [
            {"id": "1", "name": "Org Unit 1"}
        ]

        with patch("hexa.workspaces.utils.DHIS2", return_value=dhis2_mock):
            response = self.run_query(
                """
                query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!, $type: String!) {
                connectionBySlug(workspaceSlug:$workspaceSlug, connectionSlug: $connectionSlug){
                    ... on DHIS2Connection {
                        queryMetadata(type: $type) {
                                items {
                                        id
                                        name
                                      }
                                error
                            }
                        }
                    }
                }
                """,
                variables={
                    "workspaceSlug": self.WORKSPACE.slug,
                    "connectionSlug": "dhis2-connection-1",
                    "type": "ORGANISATION_UNITS",
                },
            )

            self.assertEqual(
                response["data"],
                {
                    "connectionBySlug": {
                        "queryMetadata": {
                            "items": [{"id": "1", "name": "Org Unit 1"}],
                            "error": None,
                        }
                    }
                },
            )

    def test_get_s3_connection(self):
        self.client.force_login(self.USER_JIM)

        connection = Connection.objects.create_if_has_perm(
            self.USER_JIM,
            self.WORKSPACE,
            name="S3 connection 1",
            slug="s3-connection-1",
            connection_type=ConnectionType.S3,
        )
        connection.set_fields(
            self.USER_JIM,
            [
                {
                    "code": "access_key",
                    "value": "access_key",
                    "secret": True,
                },
                {"code": "secret_key", "value": "secret_key", "secret": True},
                {"code": "region", "value": "region", "secret": False},
            ],
        )
        connection.save()

        response = self.run_query(
            """
            query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!) {
            connectionBySlug(workspaceSlug:$workspaceSlug, connectionSlug: $connectionSlug){
                ... on S3Connection {
                    name
                    id
                }
            }
            }
            """,
            variables={
                "workspaceSlug": self.WORKSPACE.slug,
                "connectionSlug": "s3-connection-1",
            },
        )
        self.assertEqual(
            response["data"],
            {
                "connectionBySlug": {
                    "name": "S3 connection 1",
                    "id": str(connection.id),
                }
            },
        )

    def test_get_org_units_no_connection(self):  # noqa
        self.client.force_login(self.USER_JIM)
        response = self.run_query(
            """
            query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!, $type: String!) {
            connectionBySlug(workspaceSlug:$workspaceSlug, connectionSlug: $connectionSlug){
                ... on DHIS2Connection {
                    queryMetadata(type: $type) {
                            items {
                                    id
                                    name
                                  }
                            error
                        }
                    }
                }
            }
            """,
            variables={
                "workspaceSlug": self.WORKSPACE.slug,
                "connectionSlug": "dhis2-connection-1",
                "type": "ORGANISATION_UNITS",
            },
        )
        self.assertEqual(response["data"], {"connectionBySlug": None})

    def test_get_org_units_no_permission(self):
        self.client.force_login(self.USER_SERENA)
        dhis2_mock = MagicMock()
        dhis2_mock.meta.organisation_units.return_value = [
            {"id": "1", "name": "Org Unit 1"}
        ]

        with patch("hexa.workspaces.utils.DHIS2", return_value=dhis2_mock):
            response = self.run_query(
                """
                query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!, $type: String!) {
                connectionBySlug(workspaceSlug:$workspaceSlug, connectionSlug: $connectionSlug){
                    ... on DHIS2Connection {
                        queryMetadata(type: $type) {
                                items {
                                        id
                                        name
                                      }
                                error
                            }
                        }
                    }
                }
                """,
                variables={
                    "workspaceSlug": self.WORKSPACE.slug,
                    "connectionSlug": "dhis2-connection-1",
                    "type": "ORGANISATION_UNITS",
                },
            )
            self.assertEqual(response["data"], {"connectionBySlug": None})

    def test_connection_error(self):
        self.client.force_login(self.USER_JIM)

        dhis2_mock = MagicMock()
        dhis2_mock.meta.organisation_units.side_effect = DHIS2Error("Connection error")

        with patch("hexa.workspaces.utils.DHIS2", return_value=dhis2_mock):
            response = self.run_query(
                """
                query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!, $type: String!) {
                connectionBySlug(workspaceSlug:$workspaceSlug, connectionSlug: $connectionSlug){
                    ... on DHIS2Connection {
                        queryMetadata(type: $type) {
                                items {
                                        id
                                        name
                                      }
                                error
                            }
                        }
                    }
                }
                """,
                variables={
                    "workspaceSlug": self.WORKSPACE.slug,
                    "connectionSlug": "dhis2-connection-1",
                    "type": "ORGANISATION_UNITS",
                },
            )
            self.assertEqual(
                response["data"],
                {
                    "connectionBySlug": {
                        "queryMetadata": {"items": None, "error": "CONNECTION_ERROR"}
                    }
                },
            )

    def test_unkown_error(self):
        self.client.force_login(self.USER_JIM)

        dhis2_mock = MagicMock()
        dhis2_mock.meta.organisation_units.side_effect = Exception("Unknown error")

        with patch("hexa.workspaces.utils.DHIS2", return_value=dhis2_mock):
            response = self.run_query(
                """
                query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!, $type: String!) {
                connectionBySlug(workspaceSlug:$workspaceSlug, connectionSlug: $connectionSlug){
                    ... on DHIS2Connection {
                        queryMetadata(type: $type) {
                                items {
                                        id
                                        name
                                      }
                                error
                            }
                        }
                    }
                }
                """,
                variables={
                    "workspaceSlug": self.WORKSPACE.slug,
                    "connectionSlug": "dhis2-connection-1",
                    "type": "ORGANISATION_UNITS",
                },
            )
            self.assertEqual(
                response["data"],
                {
                    "connectionBySlug": {
                        "queryMetadata": {"items": None, "error": "UNKNOWN_ERROR"}
                    }
                },
            )
