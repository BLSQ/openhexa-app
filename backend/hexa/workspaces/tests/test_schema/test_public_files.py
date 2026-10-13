from django.conf import settings

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace

WORKSPACE_QUERY = """
query workspace($slug: String!) {
    workspace(slug: $slug) {
        publicFilesEnabled
        publicFilesUrl
        permissions { managePublicFiles }
    }
}
"""

UPDATE_MUTATION = """
mutation updateWorkspace($input: UpdateWorkspaceInput!) {
    updateWorkspace(input: $input) {
        success
        errors
        workspace { publicFilesEnabled }
    }
}
"""


class PublicFilesSchemaTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(name="Org")
        cls.USER_ORG_ADMIN = User.objects.create_user("org@bluesquarehub.com", "pw")
        cls.USER_WORKSPACE_ADMIN = User.objects.create_user(
            "wsadmin@bluesquarehub.com", "pw"
        )
        for user in (cls.USER_ORG_ADMIN, cls.USER_WORKSPACE_ADMIN):
            OrganizationMembership.objects.create(
                organization=cls.ORGANIZATION,
                user=user,
                role=OrganizationMembershipRole.ADMIN
                if user is cls.USER_ORG_ADMIN
                else OrganizationMembershipRole.MEMBER,
            )
        cls.WORKSPACE = create_workspace(
            cls.USER_ORG_ADMIN, name="Senegal", organization=cls.ORGANIZATION
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_WORKSPACE_ADMIN,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

    def test_workspace_fields(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(WORKSPACE_QUERY, {"slug": self.WORKSPACE.slug})
        self.assertEqual(
            {
                "publicFilesEnabled": False,
                "publicFilesUrl": f"{settings.BASE_URL}/files/public/{self.WORKSPACE.slug}/",
                "permissions": {"managePublicFiles": False},
            },
            r["data"]["workspace"],
        )

        self.client.force_login(self.USER_ORG_ADMIN)
        r = self.run_query(WORKSPACE_QUERY, {"slug": self.WORKSPACE.slug})
        self.assertTrue(r["data"]["workspace"]["permissions"]["managePublicFiles"])

    def test_org_admin_toggles_public_files(self):
        self.client.force_login(self.USER_ORG_ADMIN)
        for enabled in (True, False):
            r = self.run_query(
                UPDATE_MUTATION,
                {"input": {"slug": self.WORKSPACE.slug, "publicFilesEnabled": enabled}},
            )
            self.assertEqual(
                {
                    "success": True,
                    "errors": [],
                    "workspace": {"publicFilesEnabled": enabled},
                },
                r["data"]["updateWorkspace"],
            )
            self.WORKSPACE.refresh_from_db()
            self.assertEqual(enabled, self.WORKSPACE.public_files_enabled)

    def test_workspace_admin_cannot_toggle_public_files(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            UPDATE_MUTATION,
            {"input": {"slug": self.WORKSPACE.slug, "publicFilesEnabled": True}},
        )
        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"], "workspace": None},
            r["data"]["updateWorkspace"],
        )
        self.WORKSPACE.refresh_from_db()
        self.assertFalse(self.WORKSPACE.public_files_enabled)

    def test_workspace_admin_still_updates_other_fields(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            UPDATE_MUTATION,
            {"input": {"slug": self.WORKSPACE.slug, "description": "Updated"}},
        )
        self.assertTrue(r["data"]["updateWorkspace"]["success"])
