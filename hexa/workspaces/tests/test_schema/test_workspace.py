import uuid
from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.files.tests.mocks.mockgcp import mock_gcp_storage
from hexa.user_management.models import Feature, FeatureFlag, User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WorkspaceTest(GraphQLTestCase):
    USER_SABRINA = None
    USER_REBECCA = None
    USER_JULIA = None
    USER_WORKSPACE_ADMIN = None
    WORKSPACE = None

    @classmethod
    @mock_gcp_storage
    def setUpTestData(cls):
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )

        cls.USER_REBECCA = User.objects.create_user(
            "rebecca@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_JULIA = User.objects.create_user(
            "julia@bluesquarehub.com", "juliaspassword"
        )
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_JULIA
        )

        cls.USER_WORKSPACE_ADMIN = User.objects.create_user(
            "workspaceroot@bluesquarehub.com",
            "workspace",
        )

        with patch("hexa.workspaces.models.create_database"):
            cls.WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.USER_JULIA,
                name="Senegal Workspace",
                description="This is a workspace for Senegal",
                countries=[{"code": "AL"}],
            )
            cls.WORKSPACE_2 = Workspace.objects.create_if_has_perm(
                cls.USER_JULIA,
                name="Burundi Workspace",
                description="This is a workspace for Burundi",
                countries=[{"code": "AD"}],
            )

        cls.WORKSPACE_MEMBERSHIP = WorkspaceMembership.objects.create(
            user=cls.USER_REBECCA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.VIEWER,
        )

        cls.WORKSPACE_MEMBERSHIP_2 = WorkspaceMembership.objects.create(
            user=cls.USER_WORKSPACE_ADMIN,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

    @mock_gcp_storage
    def test_create_workspace_denied(self):
        self.client.force_login(self.USER_SABRINA)
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
            {"success": False, "errors": ["PERMISSION_DENIED"], "workspace": None},
            r["data"]["createWorkspace"],
        )

    @mock_gcp_storage
    def test_create_workspace(self):
        with patch("hexa.workspaces.models.create_database"):
            self.client.force_login(self.USER_JULIA)
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

    @mock_gcp_storage
    def test_create_workspace_with_country(self):
        with patch("hexa.workspaces.models.create_database"):
            self.client.force_login(self.USER_JULIA)
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

    @mock_gcp_storage
    def test_get_workspace_not_member(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            query workspace($slug: String!) {
                workspace(slug: $slug) {
                    name
                }
            }
            """,
            {"slug": self.WORKSPACE.slug},
        )
        self.assertIsNone(
            r["data"]["workspace"],
        )

    def test_get_workspace(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            query workspace($slug: String!) {
                workspace(slug: $slug) {
                    name
                }
            }
            """,
            {"slug": self.WORKSPACE.slug},
        )
        self.assertEqual(
            {"name": self.WORKSPACE.name},
            r["data"]["workspace"],
        )

    def test_get_workspaces(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            query workspaces($page:Int!, $perPage:Int!) {
                workspaces(page:$page, perPage:$perPage) {
                   totalItems
                   totalPages
                   items {
                        slug
                        name
                   }
                }
            }
            """,
            {"page": 1, "perPage": 1},
        )

        self.assertEqual(
            {
                "totalItems": 1,
                "totalPages": 1,
                "items": [{"slug": self.WORKSPACE.slug, "name": self.WORKSPACE.name}],
            },
            r["data"]["workspaces"],
        )

    def test_update_workspace_not_found(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation updateWorkspace($input:UpdateWorkspaceInput!) {
                updateWorkspace(input: $input) {
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
                    "slug": "c02704ff-541f-4519-8619-34da7acc010b",
                    "name": "Cameroon workspace",
                    "description": "Description",
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["NOT_FOUND"], "workspace": None},
            r["data"]["updateWorkspace"],
        )

    def test_update_workspace(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation updateWorkspace($input:UpdateWorkspaceInput!) {
                updateWorkspace(input: $input) {
                    success
                    workspace {
                        description
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "slug": self.WORKSPACE.slug,
                    "description": "This is a test for updating workspace description",
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "workspace": {
                    "description": "This is a test for updating workspace description"
                },
            },
            r["data"]["updateWorkspace"],
        )

    def test_delete_workspace_not_found(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation deleteWorkspace($input: DeleteWorkspaceInput!) {
                deleteWorkspace(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "slug": self.WORKSPACE.slug,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["NOT_FOUND"],
            },
            r["data"]["deleteWorkspace"],
        )

    @patch("hexa.workspaces.models.delete_database")
    def test_delete_workspace(self, mock_delete_database):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation deleteWorkspace($input: DeleteWorkspaceInput!) {
                deleteWorkspace(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "slug": self.WORKSPACE.slug,
                }
            },
        )
        self.assertTrue(mock_delete_database.called)
        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["deleteWorkspace"],
        )

    def test_create_workspace_member_workspace_not_found(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation inviteWorkspaceMember($input: InviteWorkspaceMemberInput!) {
                inviteWorkspaceMember(input: $input) {
                    success
                    errors
                    workspaceMembership {
                        id
                        user {
                          email
                        }
                    }
                }
            }

            """,
            {
                "input": {
                    "workspaceSlug": str(uuid.uuid4()),
                    "userEmail": "root@openhexa.com",
                    "role": WorkspaceMembershipRole.EDITOR,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["WORKSPACE_NOT_FOUND"],
                "workspaceMembership": None,
            },
            r["data"]["inviteWorkspaceMember"],
        )

    def test_create_workspace_member_member_not_found(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation inviteWorkspaceMember($input: InviteWorkspaceMemberInput!) {
                inviteWorkspaceMember(input: $input) {
                    success
                    errors
                    workspaceMembership {
                        id
                        user {
                          email
                        }
                    }
                }
            }

            """,
            {
                "input": {
                    "workspaceSlug": self.WORKSPACE.slug,
                    "userEmail": "unknown@openhexa.com",
                    "role": WorkspaceMembershipRole.EDITOR,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["USER_NOT_FOUND"],
                "workspaceMembership": None,
            },
            r["data"]["inviteWorkspaceMember"],
        )

    def test_create_workspace_member_workspace_already_exist(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation inviteWorkspaceMember($input: InviteWorkspaceMemberInput!) {
                inviteWorkspaceMember(input: $input) {
                    success
                    errors
                }
            }

            """,
            {
                "input": {
                    "workspaceSlug": self.WORKSPACE.slug,
                    "userEmail": "rebecca@bluesquarehub.com",
                    "role": WorkspaceMembershipRole.EDITOR,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["ALREADY_EXISTS"],
            },
            r["data"]["inviteWorkspaceMember"],
        )

    def test_get_workspace_members(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            query workspaceById($slug: String!) {
                workspace(slug: $slug) {
                    members {
                        items {
                            user {
                                id
                            }
                        }
                    }
                }
            }
            """,
            {"slug": self.WORKSPACE.slug},
        )

        self.assertEqual(
            {
                "items": [
                    {"user": {"id": str(self.USER_WORKSPACE_ADMIN.id)}},
                    {"user": {"id": str(self.USER_REBECCA.id)}},
                    {"user": {"id": str(self.USER_JULIA.id)}},
                ],
            },
            r["data"]["workspace"]["members"],
        )

    def test_delete_workspace_member_not_found(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation deleteWorkspaceMember($input: DeleteWorkspaceMemberInput!) {
                deleteWorkspaceMember(input: $input) {
                    success
                    errors
                }
            }

            """,
            {
                "input": {
                    "membershipId": str(uuid.uuid4()),
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["MEMBERSHIP_NOT_FOUND"],
            },
            r["data"]["deleteWorkspaceMember"],
        )

    def test_delete_workspace_member_permission_denied(self):
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
            mutation deleteWorkspaceMember($input: DeleteWorkspaceMemberInput!) {
                deleteWorkspaceMember(input: $input) {
                    success
                    errors
                }
            }

            """,
            {
                "input": {
                    "membershipId": str(self.WORKSPACE_MEMBERSHIP.id),
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["deleteWorkspaceMember"],
        )

    def test_delete_workspace_member(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation deleteWorkspaceMember($input: DeleteWorkspaceMemberInput!) {
                deleteWorkspaceMember(input: $input) {
                    success
                    errors
                }
            }

            """,
            {
                "input": {
                    "membershipId": str(self.WORKSPACE_MEMBERSHIP.id),
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["deleteWorkspaceMember"],
        )

    def test_update_workspace_member_role_membership_not_found(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation updateWorkspaceMember($input: UpdateWorkspaceMemberInput!) {
                updateWorkspaceMember(input: $input) {
                    success
                    errors
                    workspaceMembership {
                        id
                        role
                    }
                }
            }

            """,
            {
                "input": {
                    "membershipId": str(uuid.uuid4()),
                    "role": WorkspaceMembershipRole.EDITOR,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["MEMBERSHIP_NOT_FOUND"],
                "workspaceMembership": None,
            },
            r["data"]["updateWorkspaceMember"],
        )

    def test_update_workspace_member_role_permission_denied(self):
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
            mutation updateWorkspaceMember($input: UpdateWorkspaceMemberInput!) {
                updateWorkspaceMember(input: $input) {
                    success
                    errors
                    workspaceMembership {
                        id
                        role
                    }
                }
            }

            """,
            {
                "input": {
                    "membershipId": str(self.WORKSPACE_MEMBERSHIP.id),
                    "role": WorkspaceMembershipRole.EDITOR,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
                "workspaceMembership": None,
            },
            r["data"]["updateWorkspaceMember"],
        )

    def test_update_workspace_member_role(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation updateWorkspaceMember($input: UpdateWorkspaceMemberInput!) {
                updateWorkspaceMember(input: $input) {
                    success
                    errors
                    workspaceMembership {
                        id
                        role
                    }
                }
            }

            """,
            {
                "input": {
                    "membershipId": str(self.WORKSPACE_MEMBERSHIP_2.id),
                    "role": WorkspaceMembershipRole.EDITOR,
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "workspaceMembership": {
                    "id": str(self.WORKSPACE_MEMBERSHIP_2.id),
                    "role": WorkspaceMembershipRole.EDITOR,
                },
            },
            r["data"]["updateWorkspaceMember"],
        )
