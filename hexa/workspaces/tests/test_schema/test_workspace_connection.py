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
