from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class WorkspaceTest(GraphQLTestCase):
    USER_SABRINA = None
    USER_ADMIN = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_ADMIN = User.objects.create_user(
            "rebecca@bluesquarehub.com", "standardpassword", is_superuser=True
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Senegal Workspace",
            description="This is a workspace for Senegal",
            countries=[{"code": "AL"}],
        )
        cls.WORKSPACE_2 = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Burundi Workspace",
            description="This is a workspace for Burundi",
            countries=[{"code": "AD"}],
        )

    def test_create_workspace_denied(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation createWorkspace($input:CreateWorkspaceInput!) {
                createWorkspace(input: $input) {
                    success
                    workspace {
                        id
                        name
                        description
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "name": "Cameroon workspace",
                    "description": "Description",
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"], "workspace": None},
            r["data"]["createWorkspace"],
        )

    def test_create_workspace(self):
        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            mutation createWorkspace($input:CreateWorkspaceInput!) {
                createWorkspace(input: $input) {
                    success
                    workspace {
                        name
                        description
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "name": "Cameroon workspace",
                    "description": "Description",
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "workspace": {
                    "name": "Cameroon workspace",
                    "description": "Description",
                },
            },
            r["data"]["createWorkspace"],
        )

    def test_create_workspace_with_country(self):
        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            mutation createWorkspace($input:CreateWorkspaceInput!) {
                createWorkspace(input: $input) {
                    success
                    workspace {
                        name
                        description
                        countries {
                          code
                        }
                    }
                   
                    errors
                }
            }
            """,
            {
                "input": {
                    "name": "Cameroon workspace",
                    "description": "Description",
                    "countries": [{"code": "AD"}],
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "workspace": {
                    "name": "Cameroon workspace",
                    "description": "Description",
                    "countries": [{"code": "AD"}],
                },
            },
            r["data"]["createWorkspace"],
        )

    def test_get_workspace_not_member(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            query workspaceById($id: String!) {
                workspace(id: $id) {
                    id
                    name
                }
            }
            """,
            {"id": str(self.WORKSPACE.id)},
        )
        self.assertIsNone(
            r["data"]["workspace"],
        )

    def test_get_workspace_empty(self):
        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            query workspaceById($id: String!) {
                workspace(id: $id) {
                    id
                    name
                }
            }
            """,
            {"id": str(self.WORKSPACE.id)},
        )
        self.assertEqual(
            {"id": str(self.WORKSPACE.id), "name": self.WORKSPACE.name},
            r["data"]["workspace"],
        )

    def test_get_workspaces(self):
        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            query workspaces($page:Int!, $perPage:Int!) {
                workspaces(page:$page, perPage:$perPage) {
                   totalItems
                   totalPages
                   items {
                    id
                    name
                   }
                }
            }
            """,
            {"page": 1, "perPage": 1},
        )

        self.assertEqual(
            {
                "totalItems": 2,
                "totalPages": 2,
                "items": [
                    {"id": str(self.WORKSPACE_2.id), "name": self.WORKSPACE_2.name}
                ],
            },
            r["data"]["workspaces"],
        )
