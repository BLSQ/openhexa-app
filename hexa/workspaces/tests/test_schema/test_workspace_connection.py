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
        self.client.force_login(self.USER_REBECCA)
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
                            "value": None,
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
                    "fields": [{"code": "url", "secret": True, "value": None}],
                },
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
        self.client.force_login(self.USER_REBECCA)
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
        self.client.force_login(self.USER_REBECCA)
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
