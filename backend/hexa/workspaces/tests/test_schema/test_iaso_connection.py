from unittest.mock import MagicMock, patch

from openhexa.toolbox.iaso.api_client import IASOError

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
        iaso_mock.get_org_units.return_value = [{"id": 1, "name": "Org Unit 1"}]

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
                    "type": "IASO_ORG_UNITS",
                },
            )
            print(response)
            self.assertEqual(
                response["data"],
                {
                    "connectionBySlug": {
                        "queryMetadata": {
                            "items": [{"id": 1, "label": "Org Unit 1"}],
                            "error": None,
                        }
                    }
                },
            )

    def test_get_org_units_with_search(self):
        self.client.force_login(self.USER_JIM)

        iaso_mock = MagicMock()
        iaso_mock.get_org_units.return_value = [
            {"id": 1, "name": "Org Unit 1"},
        ]

        with patch("hexa.workspaces.utils.IASO", return_value=iaso_mock):
            response = self.run_query(
                """
                query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!, $type: IASOMetadataType!, $search: String!) {
                connectionBySlug(workspaceSlug:$workspaceSlug, connectionSlug: $connectionSlug){
                    ... on IASOConnection {
                        queryMetadata(type: $type, search: $search) {
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
                    "type": "IASO_ORG_UNITS",
                    "search": "Org Unit 1",
                },
            )
            self.assertEqual(
                response["data"],
                {
                    "connectionBySlug": {
                        "queryMetadata": {
                            "items": [{"id": 1, "label": "Org Unit 1"}],
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
                {"id": 1, "name": "Org Unit 1"},
                {"id": 2, "name": "Org Unit 2"},
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
                    "type": "IASO_ORG_UNITS",
                },
            )
            self.assertEqual(
                response["data"]["connectionBySlug"]["queryMetadata"],
                {
                    "items": [
                        {"id": 1, "label": "Org Unit 1"},
                        {"id": 2, "label": "Org Unit 2"},
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
        iaso_mock.get_projects.return_value = [
            {
                "id": 2,
                "name": "Pathways Senegal Yux",
                "app_id": "pathways.senegal.yux",
                "feature_flags": [
                    {
                        "id": 3,
                        "name": "GPS point for each form",
                        "code": "TAKE_GPS_ON_FORM",
                    },
                    {
                        "id": 7,
                        "name": "Mobile: Show data collection screen",
                        "code": "DATA_COLLECTION",
                    },
                    {
                        "id": 12,
                        "name": "Mobile: Finalized forms are read only",
                        "code": "MOBILE_FINALIZED_FORM_ARE_READ",
                    },
                    {
                        "id": 4,
                        "name": "Authentication",
                        "code": "REQUIRE_AUTHENTICATION",
                    },
                ],
                "created_at": 1710153966.532745,
                "updated_at": 1717664805.185712,
                "needs_authentication": True,
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
                    "type": "PROJECTS",
                },
            )
            self.assertEqual(
                response["data"],
                {
                    "connectionBySlug": {
                        "queryMetadata": {
                            "items": [
                                {
                                    "id": 2,
                                    "label": "Pathways Senegal Yux",
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
        iaso_mock.get_forms.return_value = [
            {
                "id": 62,
                "name": "Form2",
                "form_id": "pathways_senegal_yux",
                "device_field": "deviceid",
                "location_field": "",
            }
        ]

        with patch("hexa.workspaces.utils.IASO", return_value=iaso_mock):
            response = self.run_query(
                """
                query getConnectionBySlug(
                    $workspaceSlug: String!, 
                    $connectionSlug: String!, 
                    $type: IASOMetadataType!,
                    $filters: [IASOQueryFilterInput!]
                ) {
                    connectionBySlug(workspaceSlug: $workspaceSlug, connectionSlug: $connectionSlug) {
                        ... on IASOConnection {
                            queryMetadata(type: $type, filters: $filters) {
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
                    "filters": [
                        {"type": "org_units", "value": [1, 2]},
                        {"type": "projects", "value": [5]},
                    ],
                },
            )
            self.assertEqual(
                response["data"],
                {
                    "connectionBySlug": {
                        "queryMetadata": {
                            "items": [
                                {
                                    "id": 62,
                                    "label": "Form2",
                                }
                            ],
                            "error": None,
                        }
                    }
                },
            )

    def test_get_org_units_raises_request_error(self):
        self.client.force_login(self.USER_JIM)

        iaso_mock = MagicMock()
        iaso_mock.get_org_units.side_effect = IASOError("500 error")

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
                    "type": "IASO_ORG_UNITS",
                },
            )
            self.assertEqual(
                response["data"],
                {
                    "connectionBySlug": {
                        "queryMetadata": {
                            "items": [],
                            "error": "REQUEST_ERROR",
                        }
                    }
                },
            )
