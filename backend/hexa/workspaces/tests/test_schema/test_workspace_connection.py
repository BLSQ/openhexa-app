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


class ConnectionTest(GraphQLTestCase):
    USER_SABRINA = None
    USER_ADMIN = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_REBECCA = User.objects.create_user(
            "rebecca@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_VIEWER = User.objects.create_user(
            "viewer@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com", "standardpassword", is_superuser=True
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Senegal Workspace",
            description="This is a workspace for Senegal",
            countries=[{"code": "AL"}],
        )

        cls.WORKSPACE_MEMBERSHIP_SABRINA = WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_SABRINA,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.WORKSPACE_MEMBERSHIP_REBECCA = WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_REBECCA,
            role=WorkspaceMembershipRole.EDITOR,
        )
        cls.WORKSPACE_MEMBERSHIP_VIEWER = WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_VIEWER,
            role=WorkspaceMembershipRole.VIEWER,
        )
        cls.WORKSPACE_CONNECTION = Connection.objects.create_if_has_perm(
            cls.USER_SABRINA,
            cls.WORKSPACE,
            name="DB",
            description="Connection's description",
            connection_type=ConnectionType.POSTGRESQL,
        )

        cls.WORKSPACE_2 = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Burundi Workspace",
            description="This is a workspace for Burundi",
            countries=[{"code": "AD"}],
        )

        cls.WORKSPACE_CONNECTION_2 = Connection.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.WORKSPACE_2,
            name="DB",
            description="Connection's description",
            connection_type=ConnectionType.CUSTOM,
        )

    def test_create_connection_non_member(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation createConnection($input:CreateConnectionInput!) {
                createConnection(input: $input) {
                    success
                    connection {
                        id
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": str(self.WORKSPACE_2.slug),
                    "name": "Connection",
                    "type": ConnectionType.CUSTOM,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["WORKSPACE_NOT_FOUND"],
                "connection": None,
            },
            r["data"]["createConnection"],
        )

    def test_create_connection_permission_denied(self):
        self.client.force_login(self.USER_VIEWER)
        r = self.run_query(
            """
            mutation createConnection($input:CreateConnectionInput!) {
                createConnection(input: $input) {
                    success
                    connection {
                        id
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": str(self.WORKSPACE.slug),
                    "name": "Connection",
                    "type": ConnectionType.CUSTOM,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
                "connection": None,
            },
            r["data"]["createConnection"],
        )

    def test_create_connection_invalid_fields(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation createConnection($input:CreateConnectionInput!) {
                createConnection(input: $input) {
                    success
                    connection {
                        name
                        slug
                        type
                        fields {
                            code
                            value
                            secret
                        }
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": str(self.WORKSPACE.slug),
                    "name": "Connection",
                    "slug": "con",
                    "type": ConnectionType.CUSTOM,
                    "fields": [
                        {
                            "code": "this is an invalid field",
                            "value": "http://localhost",
                            "secret": False,
                        },
                        {
                            "code": "password",
                            "value": "pA$$",
                            "secret": True,
                        },
                    ],
                }
            },
        )

        self.assertEqual(
            {"success": False, "connection": None, "errors": ["INVALID_SLUG"]},
            r["data"]["createConnection"],
        )
        with self.assertRaises(Connection.DoesNotExist):
            Connection.objects.get(slug="con")

    def test_create_connection(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation createConnection($input:CreateConnectionInput!) {
                createConnection(input: $input) {
                    success
                    connection {
                        name
                        slug
                        type
                        fields {
                            code
                            value
                            secret
                        }
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": str(self.WORKSPACE.slug),
                    "name": "Connection",
                    "slug": "con",
                    "type": ConnectionType.CUSTOM,
                    "fields": [
                        {
                            "code": "url",
                            "value": "http://localhost",
                            "secret": False,
                        },
                        {
                            "code": "password",
                            "value": "pA$$",
                            "secret": True,
                        },
                    ],
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "connection": {
                    "name": "Connection",
                    "slug": "con",
                    "type": "CUSTOM",
                    "fields": [
                        {
                            "code": "url",
                            "secret": False,
                            "value": "http://localhost",
                        },
                        {
                            "code": "password",
                            "secret": True,
                            "value": "pA$$",
                        },
                    ],
                },
            },
            r["data"]["createConnection"],
        )

    def test_update_connection(self):
        self.client.force_login(self.USER_SABRINA)
        self.WORKSPACE_CONNECTION.set_fields(
            self.USER_SABRINA,
            [
                {
                    "code": "url",
                    "value": "http://localhost",
                    "secret": False,
                },
                {
                    "code": "password",
                    "value": "pA$$",
                    "secret": True,
                },
            ],
        )
        r = self.run_query(
            """
            mutation updateConnection($input:UpdateConnectionInput!) {
                updateConnection(input: $input) {
                    success
                    connection {
                        name
                        description
                        fields {
                            code
                            value
                            secret
                        }
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(self.WORKSPACE_CONNECTION.id),
                    "name": "DB (updated)",
                    "fields": [
                        {
                            "code": "url",
                            "value": "http://otherhost",
                            "secret": True,
                        },
                    ],
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "connection": {
                    "name": "DB (updated)",
                    "description": "Connection's description",
                    "fields": [
                        {"code": "url", "secret": True, "value": "http://otherhost"}
                    ],
                },
            },
            r["data"]["updateConnection"],
        )

    def test_secret_field_no_value_for_viewer(self):
        self.client.force_login(self.USER_VIEWER)
        self.WORKSPACE_CONNECTION.set_fields(
            self.USER_SABRINA,
            [
                {
                    "code": "url",
                    "value": "http://localhost",
                    "secret": False,
                },
                {
                    "code": "password",
                    "value": "pA$$",
                    "secret": True,
                },
            ],
        )
        r = self.run_query(
            """
            query getConnection($connectionId: UUID!) {
                connection(id: $connectionId) {
                    fields {
                        code
                        value
                        secret
                    }
                    
                }
            }
            """,
            {
                "connectionId": str(self.WORKSPACE_CONNECTION.id),
            },
        )
        self.assertEqual(
            {
                "connection": {
                    "fields": [
                        {
                            "code": "url",
                            "value": "http://localhost",
                            "secret": False,
                        },
                        {
                            "code": "password",
                            "value": None,
                            "secret": True,
                        },
                    ]
                },
            },
            r["data"],
        )

    def test_update_connection_viewer_permission_denied(self):
        self.WORKSPACE_CONNECTION.set_fields(
            self.USER_SABRINA,
            [
                {
                    "code": "url",
                    "value": "http://localhost",
                    "secret": False,
                },
                {
                    "code": "password",
                    "value": "pa$$",
                    "secret": True,
                },
            ],
        )

        self.client.force_login(self.USER_VIEWER)
        r = self.run_query(
            """
            mutation updateConnection($input:UpdateConnectionInput!) {
                updateConnection(input: $input) {
                    success
                    connection {
                        name
                        description
                        fields {
                            code
                            value
                            secret
                        }
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(self.WORKSPACE_CONNECTION.id),
                    "name": "DB (updated)",
                    "fields": [
                        {
                            "code": "password",
                            "value": "newPass",
                            "secret": False,
                        },
                    ],
                }
            },
        )
        self.assertEqual(
            {
                "connection": None,
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["updateConnection"],
        )

    def test_create_connection_invalid_slug(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation createConnection($input:CreateConnectionInput!) {
                createConnection(input: $input) {
                    success
                    connection {
                        name
                        slug
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": str(self.WORKSPACE.slug),
                    "name": "Connection",
                    "slug": "con?'-",
                    "type": ConnectionType.CUSTOM,
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["INVALID_SLUG"], "connection": None},
            r["data"]["createConnection"],
        )

    def test_create_connection_no_slug(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation createConnection($input:CreateConnectionInput!) {
                createConnection(input: $input) {
                    success
                    connection {
                        name
                        slug
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": str(self.WORKSPACE.slug),
                    "name": "Connection",
                    "type": ConnectionType.CUSTOM,
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "connection": {"name": "Connection", "slug": "connection"},
            },
            r["data"]["createConnection"],
        )

    def test_get_connection_by_slug(self):
        self.client.force_login(self.USER_SABRINA)
        self.WORKSPACE_CONNECTION.set_fields(
            self.USER_SABRINA,
            [
                {
                    "code": "url",
                    "value": "http://localhost",
                    "secret": False,
                },
                {
                    "code": "password",
                    "value": "pA$$",
                    "secret": True,
                },
            ],
        )
        r = self.run_query(
            """
            query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!) {
                connectionBySlug(workspaceSlug:$workspaceSlug, connectionSlug: $connectionSlug) {
                    fields {
                        code
                        value
                        secret
                    }
                    
                }
            }
            """,
            {
                "workspaceSlug": self.WORKSPACE.slug,
                "connectionSlug": self.WORKSPACE_CONNECTION.slug,
            },
        )
        self.assertEqual(
            {
                "connectionBySlug": {
                    "fields": [
                        {
                            "code": "url",
                            "value": "http://localhost",
                            "secret": False,
                        },
                        {
                            "code": "password",
                            "value": "pA$$",
                            "secret": True,
                        },
                    ]
                },
            },
            r["data"],
        )

    def test_get_connection_by_slug_not_found(self):
        self.client.force_login(self.USER_SABRINA)
        self.WORKSPACE_CONNECTION.set_fields(
            self.USER_SABRINA,
            [
                {
                    "code": "url",
                    "value": "http://localhost",
                    "secret": False,
                },
                {
                    "code": "password",
                    "value": "pA$$",
                    "secret": True,
                },
            ],
        )
        r = self.run_query(
            """
            query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!) {
                connectionBySlug(workspaceSlug:$workspaceSlug, connectionSlug: $connectionSlug) {
                    fields {
                        code
                        value
                        secret
                    }
                    
                }
            }
            """,
            {"workspaceSlug": self.WORKSPACE.slug, "connectionSlug": "random_slug"},
        )
        self.assertEqual(
            {
                "connectionBySlug": None,
            },
            r["data"],
        )

    def test_update_connection_invalid_slug(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation updateConnection($input:UpdateConnectionInput!) {
                updateConnection(input: $input) {
                    success
                    connection {
                        slug
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(self.WORKSPACE_CONNECTION.id),
                    "slug": "DB (updated)",
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["INVALID_SLUG"],
                "connection": None,
            },
            r["data"]["updateConnection"],
        )

    def test_update_connection_permission_denied(self):
        self.client.force_login(self.USER_VIEWER)
        r = self.run_query(
            """
            mutation updateConnection($input:UpdateConnectionInput!) {
                updateConnection(input: $input) {
                    success
                    connection {
                        name
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(self.WORKSPACE_CONNECTION.id),
                    "name": "DB (updated)",
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
                "connection": None,
            },
            r["data"]["updateConnection"],
        )

    def test_delete_connection_permission_denied(self):
        self.client.force_login(self.USER_VIEWER)
        r = self.run_query(
            """
            mutation deleteConnection($input:DeleteConnectionInput!) {
                deleteConnection(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(self.WORKSPACE_CONNECTION.id),
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["deleteConnection"],
        )

    def test_delete_connection(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation deleteConnection($input:DeleteConnectionInput!) {
                deleteConnection(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(self.WORKSPACE_CONNECTION.id),
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["deleteConnection"],
        )


TEST_CONNECTION_MUTATION = """
    mutation testConnection($input: TestConnectionInput!) {
        testConnection(input: $input) {
            success
            error
        }
    }
"""


class TestConnectionTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com",
            "standardpassword",
            is_superuser=True,
        )
        cls.USER_EDITOR = User.objects.create_user(
            "editor@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_VIEWER = User.objects.create_user(
            "viewer@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_OUTSIDER = User.objects.create_user(
            "outsider@bluesquarehub.com",
            "standardpassword",
        )
        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Test Workspace",
            description="Workspace for testing connections",
            countries=[{"code": "AL"}],
        )
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_EDITOR,
            role=WorkspaceMembershipRole.EDITOR,
        )
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_VIEWER,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def _build_input(self, connection_type, fields):
        return {
            "input": {
                "workspaceSlug": self.WORKSPACE.slug,
                "type": connection_type,
                "fields": fields,
            }
        }

    DHIS2_FIELDS = [
        {"code": "url", "value": "https://play.dhis2.org", "secret": False},
        {"code": "username", "value": "admin", "secret": False},
        {"code": "password", "value": "district", "secret": True},
    ]

    def test_test_connection_anonymous(self):
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input("DHIS2", self.DHIS2_FIELDS),
        )
        self.assertIsNotNone(r.get("errors"))

    def test_test_connection_permission_denied_viewer(self):
        self.client.force_login(self.USER_VIEWER)
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input("DHIS2", self.DHIS2_FIELDS),
        )
        self.assertEqual(False, r["data"]["testConnection"]["success"])
        self.assertEqual("PERMISSION_DENIED", r["data"]["testConnection"]["error"])

    def test_test_connection_permission_denied_outsider(self):
        self.client.force_login(self.USER_OUTSIDER)
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input("DHIS2", self.DHIS2_FIELDS),
        )
        self.assertEqual(False, r["data"]["testConnection"]["success"])
        self.assertEqual("NOT_FOUND", r["data"]["testConnection"]["error"])

    def test_test_connection_unsupported_type(self):
        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input(
                "CUSTOM",
                [
                    {"code": "url", "value": "https://example.com", "secret": False},
                ],
            ),
        )
        self.assertEqual(False, r["data"]["testConnection"]["success"])
        self.assertIn("not supported", r["data"]["testConnection"]["error"])

    @patch("hexa.workspaces.connection_utils.DHIS2")
    def test_test_connection_dhis2_success(self, mock_dhis2_class):
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.me.return_value = {"username": "admin"}
        mock_dhis2_class.return_value = mock_client

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input("DHIS2", self.DHIS2_FIELDS),
        )
        self.assertEqual(
            {"success": True, "error": None},
            r["data"]["testConnection"],
        )
        mock_dhis2_class.assert_called_once_with(
            url="https://play.dhis2.org", username="admin", password="district"
        )

    @patch("hexa.workspaces.connection_utils.DHIS2")
    def test_test_connection_dhis2_unreachable(self, mock_dhis2_class):
        mock_client = MagicMock()
        mock_client.ping.return_value = False
        mock_dhis2_class.return_value = mock_client

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input(
                "DHIS2",
                [
                    {
                        "code": "url",
                        "value": "https://bad-url.example",
                        "secret": False,
                    },
                    {"code": "username", "value": "admin", "secret": False},
                    {"code": "password", "value": "wrong", "secret": True},
                ],
            ),
        )
        self.assertEqual(False, r["data"]["testConnection"]["success"])
        self.assertIn("not reachable", r["data"]["testConnection"]["error"])

    @patch("hexa.workspaces.connection_utils.DHIS2")
    def test_test_connection_dhis2_auth_failure(self, mock_dhis2_class):
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.me.side_effect = Exception("401 Unauthorized")
        mock_dhis2_class.return_value = mock_client

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input("DHIS2", self.DHIS2_FIELDS),
        )
        self.assertEqual(False, r["data"]["testConnection"]["success"])
        self.assertIn("401 Unauthorized", r["data"]["testConnection"]["error"])

    @patch("hexa.workspaces.connection_utils.IASO")
    def test_test_connection_iaso_success(self, mock_iaso_class):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"user_name": "demo"}
        mock_client.api_client.get.return_value = mock_response
        mock_iaso_class.return_value = mock_client

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input(
                "IASO",
                [
                    {
                        "code": "url",
                        "value": "https://iaso.example.com",
                        "secret": False,
                    },
                    {"code": "username", "value": "demo", "secret": False},
                    {"code": "password", "value": "demo", "secret": True},
                ],
            ),
        )
        self.assertEqual(
            {"success": True, "error": None},
            r["data"]["testConnection"],
        )

    @patch("hexa.workspaces.connection_utils.psycopg2")
    def test_test_connection_postgresql_success(self, mock_psycopg2):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input(
                "POSTGRESQL",
                [
                    {"code": "host", "value": "localhost", "secret": False},
                    {"code": "port", "value": "5432", "secret": False},
                    {"code": "username", "value": "user", "secret": False},
                    {"code": "password", "value": "pass", "secret": True},
                    {"code": "db_name", "value": "testdb", "secret": False},
                ],
            ),
        )
        self.assertEqual(
            {"success": True, "error": None},
            r["data"]["testConnection"],
        )
        mock_psycopg2.connect.assert_called_once_with(
            host="localhost",
            port=5432,
            user="user",
            password="pass",
            dbname="testdb",
            connect_timeout=10,
        )

    @patch("hexa.workspaces.connection_utils.psycopg2")
    def test_test_connection_postgresql_failure(self, mock_psycopg2):
        mock_psycopg2.connect.side_effect = Exception(
            "could not connect to server: Connection refused"
        )

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input(
                "POSTGRESQL",
                [
                    {"code": "host", "value": "badhost", "secret": False},
                    {"code": "port", "value": "5432", "secret": False},
                    {"code": "username", "value": "user", "secret": False},
                    {"code": "password", "value": "pass", "secret": True},
                    {"code": "db_name", "value": "testdb", "secret": False},
                ],
            ),
        )
        self.assertEqual(False, r["data"]["testConnection"]["success"])
        self.assertIn(
            "could not connect to server", r["data"]["testConnection"]["error"]
        )

    @patch("hexa.workspaces.connection_utils.boto3")
    def test_test_connection_s3_success(self, mock_boto3):
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input(
                "S3",
                [
                    {"code": "access_key_id", "value": "AKIA...", "secret": True},
                    {"code": "access_key_secret", "value": "secret", "secret": True},
                    {"code": "bucket_name", "value": "my-bucket", "secret": False},
                ],
            ),
        )
        self.assertEqual(
            {"success": True, "error": None},
            r["data"]["testConnection"],
        )
        mock_client.head_bucket.assert_called_once_with(Bucket="my-bucket")

    @patch("hexa.workspaces.connection_utils.boto3")
    def test_test_connection_s3_failure(self, mock_boto3):
        mock_client = MagicMock()
        mock_client.head_bucket.side_effect = Exception("Access Denied")
        mock_boto3.client.return_value = mock_client

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input(
                "S3",
                [
                    {"code": "access_key_id", "value": "AKIA...", "secret": True},
                    {"code": "access_key_secret", "value": "secret", "secret": True},
                    {"code": "bucket_name", "value": "bad-bucket", "secret": False},
                ],
            ),
        )
        self.assertEqual(False, r["data"]["testConnection"]["success"])
        self.assertIn("Access Denied", r["data"]["testConnection"]["error"])

    @patch("hexa.workspaces.connection_utils.gcs_storage")
    def test_test_connection_gcs_success(self, mock_gcs_storage):
        mock_client = MagicMock()
        mock_gcs_storage.Client.from_service_account_info.return_value = mock_client
        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = []

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input(
                "GCS",
                [
                    {
                        "code": "service_account_key",
                        "value": '{"type": "service_account", "project_id": "test"}',
                        "secret": True,
                    },
                    {"code": "bucket_name", "value": "my-gcs-bucket", "secret": False},
                ],
            ),
        )
        self.assertEqual(
            {"success": True, "error": None},
            r["data"]["testConnection"],
        )
        mock_client.bucket.assert_called_once_with("my-gcs-bucket")
        mock_bucket.list_blobs.assert_called_once_with(max_results=1)

    @patch("hexa.workspaces.connection_utils.gcs_storage")
    def test_test_connection_gcs_failure(self, mock_gcs_storage):
        mock_client = MagicMock()
        mock_gcs_storage.Client.from_service_account_info.return_value = mock_client
        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.side_effect = Exception("403 Forbidden")

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            TEST_CONNECTION_MUTATION,
            self._build_input(
                "GCS",
                [
                    {
                        "code": "service_account_key",
                        "value": '{"type": "service_account", "project_id": "test"}',
                        "secret": True,
                    },
                    {"code": "bucket_name", "value": "bad-bucket", "secret": False},
                ],
            ),
        )
        self.assertEqual(False, r["data"]["testConnection"]["success"])
        self.assertIn("403 Forbidden", r["data"]["testConnection"]["error"])
