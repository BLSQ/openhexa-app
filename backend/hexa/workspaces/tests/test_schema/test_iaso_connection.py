from unittest.mock import MagicMock, patch

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
            name="IASO connection 1",
            slug="iaso-connection-1",
            connection_type=ConnectionType.IASO,
        )
        connection.set_fields(
            cls.USER_JIM,
            [
                {
                    "code": "url",
                    "value": "http://127.0.0.1:8080",
                    "secret": False,
                },
                {"code": "username", "value": "jim", "secret": False},
                {"code": "password", "value": "test", "secret": True},
            ],
        )
        connection.save()

    def test_get_org_units(self):
        self.client.force_login(self.USER_JIM)

        iaso_mock = MagicMock()
        iaso_mock.get_org_units.return_value = [{"id": "1", "name": "Org Unit 1"}]

        with patch("hexa.workspaces.utils.IASO", return_value=iaso_mock):
            response = self.run_query(
                """
                query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!, $type: IASOMetadataType!) {
                connectionBySlug(workspaceSlug:$workspaceSlug, connectionSlug: $connectionSlug){
                    ... on IASOConnection {
                        queryMetadata(type: $type) {
                                items {
                                        id
                                        label
                                      }
                                error
                            }
                        }
                    }
                }
                """,
                variables={
                    "workspaceSlug": self.WORKSPACE.slug,
                    "connectionSlug": "iaso-connection-1",
                    "type": "ORG_UNITS",
                },
            )
            self.assertEqual(
                response["data"],
                {
                    "connectionBySlug": {
                        "queryMetadata": {
                            "items": [{"id": "1", "label": "Org Unit 1"}],
                            "error": None,
                        }
                    }
                },
            )

    def test_get_org_units_paged(self):
        self.client.force_login(self.USER_JIM)
        self.maxDiff = None

        iaso_mock = MagicMock()
        iaso_mock.get_org_units.return_value = {
            "pager": {"page": 1, "pageCount": 1, "total": 2},
            "items": [
                {"id": "1", "name": "Org Unit 1"},
                {"id": "2", "name": "Org Unit 2"},
            ],
        }

        with patch("hexa.workspaces.utils.IASO", return_value=iaso_mock):
            response = self.run_query(
                """
                query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!, $type: IASOMetadataType!) {
                connectionBySlug(workspaceSlug:$workspaceSlug, connectionSlug: $connectionSlug){
                    ... on IASOConnection {
                        queryMetadata(type: $type, page: 1, perPage: 2) {
                                pageNumber
                                totalItems
                                totalPages
                                items {
                                        id
                                        label
                                      }
                                error
                            }
                        }
                    }
                }
                """,
                variables={
                    "workspaceSlug": self.WORKSPACE.slug,
                    "connectionSlug": "iaso-connection-1",
                    "type": "ORG_UNITS",
                },
            )
            self.assertEqual(
                response["data"]["connectionBySlug"]["queryMetadata"],
                {
                    "items": [
                        {"id": "1", "label": "Org Unit 1"},
                        {"id": "2", "label": "Org Unit 2"},
                    ],
                    "pageNumber": 1,
                    "totalItems": 2,
                    "totalPages": 1,
                    "error": None,
                },
            )

    def test_get_projects(self):
        self.client.force_login(self.USER_JIM)

        iaso_mock = MagicMock()
        iaso_mock.get_projects.return_value = {
            "projects": [
                {
                    "id": 2,
                    "name": "Pathways Senegal Yux",
                    "app_id": "pathways.senegal.yux",
                }
            ]
        }

        with patch("hexa.workspaces.utils.IASO", return_value=iaso_mock):
            response = self.run_query(
                """
                query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!, $type: IASOMetadataType!) {
                connectionBySlug(workspaceSlug:$workspaceSlug, connectionSlug: $connectionSlug){
                    ... on IASOConnection {
                        queryMetadata(type: $type) {
                                items {
                                        id
                                        label
                                      }
                                error
                            }
                        }
                    }
                }
                """,
                variables={
                    "workspaceSlug": self.WORKSPACE.slug,
                    "connectionSlug": "iaso-connection-1",
                    "type": "ORG_UNIT_LEVELS",
                },
            )
            self.assertEqual(
                response["data"],
                {
                    "connectionBySlug": {
                        "queryMetadata": {
                            "items": [
                                {
                                    "id": "1",
                                    "label": "District",
                                }
                            ],
                            "error": None,
                        }
                    }
                },
            )

    def test_get_forms(self):
        self.client.force_login(self.USER_JIM)

        iaso_mock = MagicMock()
        iaso_mock.meta.forms.return_value = [
            {
                "id": 62,
                "name": "Senegal Recruitment (Jan 2025)",
                "form_id": "pathways_senegal_yux",
                "device_field": "deviceid",
                "location_field": "",
            }
        ]

        with patch("hexa.workspaces.utils.IASO", return_value=iaso_mock):
            response = self.run_query(
                """
                query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!, $type: IASOMetadataType!) {
                connectionBySlug(workspaceSlug:$workspaceSlug, connectionSlug: $connectionSlug){
                    ... on IASOConnection {
                        queryMetadata(type: $type) {
                                items {
                                        id
                                        label
                                      }
                                error
                            }
                        }
                    }
                }
                """,
                variables={
                    "workspaceSlug": self.WORKSPACE.slug,
                    "connectionSlug": "iaso-connection-1",
                    "type": "FORMS",
                },
            )
            print(response)
            self.assertEqual(
                response["data"],
                {
                    "connectionBySlug": {
                        "queryMetadata": {
                            "items": [
                                {
                                    "id": 62,
                                    "label": "Senegal Recruitment (Jan 2025)",
                                }
                            ],
                            "error": None,
                        }
                    }
                },
            )
