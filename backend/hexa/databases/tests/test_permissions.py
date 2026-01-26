from hexa.core.test import TestCase
from hexa.databases.permissions import view_database_credentials
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class DatabasesOrganizationPermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-databases",
            organization_type="CORPORATE",
        )

        cls.USER_ORG_OWNER = User.objects.create_user(
            "owner@bluesquarehub.com", "password"
        )
        cls.USER_ORG_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com", "password"
        )
        cls.USER_ORG_MEMBER = User.objects.create_user(
            "member@bluesquarehub.com", "password"
        )
        cls.USER_NON_ORG_MEMBER = User.objects.create_user(
            "non_member@bluesquarehub.com", "password"
        )
        cls.USER_WORKSPACE_ADMIN = User.objects.create_user(
            "workspace_admin@bluesquarehub.com", "password", is_superuser=True
        )
        cls.USER_WORKSPACE_EDITOR = User.objects.create_user(
            "workspace_editor@bluesquarehub.com", "password"
        )
        cls.USER_WORKSPACE_VIEWER = User.objects.create_user(
            "workspace_viewer@bluesquarehub.com", "password"
        )

        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_ORG_OWNER,
            role=OrganizationMembershipRole.OWNER,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_ORG_ADMIN,
            role=OrganizationMembershipRole.ADMIN,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_ORG_MEMBER,
            role=OrganizationMembershipRole.MEMBER,
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_WORKSPACE_ADMIN,
            name="Test Workspace",
            description="Test workspace for database permissions",
            organization=cls.ORGANIZATION,
        )

        cls.USER_WORKSPACE_ADMIN.is_superuser = False
        cls.USER_WORKSPACE_ADMIN.save()
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_WORKSPACE_EDITOR,
            role=WorkspaceMembershipRole.EDITOR,
        )
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_WORKSPACE_VIEWER,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def test_organization_owner_can_view_database_credentials(self):
        """Organization owners should be able to view database credentials even without workspace membership"""
        self.assertTrue(view_database_credentials(self.USER_ORG_OWNER, self.WORKSPACE))

    def test_organization_admin_can_view_database_credentials(self):
        """Organization admins should be able to view database credentials even without workspace membership"""
        self.assertTrue(view_database_credentials(self.USER_ORG_ADMIN, self.WORKSPACE))

    def test_organization_member_cannot_view_database_credentials(self):
        """Organization members should NOT be able to view database credentials without workspace membership"""
        self.assertFalse(
            view_database_credentials(self.USER_ORG_MEMBER, self.WORKSPACE)
        )

    def test_non_organization_member_cannot_view_database_credentials(self):
        """Non-organization members should NOT be able to view database credentials without workspace membership"""
        self.assertFalse(
            view_database_credentials(self.USER_NON_ORG_MEMBER, self.WORKSPACE)
        )

    def test_workspace_admin_can_view_database_credentials(self):
        """Workspace admins should be able to view database credentials through workspace membership"""
        self.assertTrue(
            view_database_credentials(self.USER_WORKSPACE_ADMIN, self.WORKSPACE)
        )

    def test_workspace_editor_can_view_database_credentials(self):
        """Workspace editors should be able to view database credentials through workspace membership"""
        self.assertTrue(
            view_database_credentials(self.USER_WORKSPACE_EDITOR, self.WORKSPACE)
        )

    def test_workspace_viewer_cannot_view_database_credentials(self):
        """Workspace viewers should NOT be able to view database credentials (only editors and admins)"""
        self.assertFalse(
            view_database_credentials(self.USER_WORKSPACE_VIEWER, self.WORKSPACE)
        )

    def test_permissions_with_null_organization(self):
        """Test permissions when workspace has no organization"""
        workspace_no_org = Workspace.objects.create(
            name="No Org Workspace",
            description="Workspace without organization",
        )
        WorkspaceMembership.objects.create(
            workspace=workspace_no_org,
            user=self.USER_WORKSPACE_ADMIN,
            role=WorkspaceMembershipRole.ADMIN,
        )
        WorkspaceMembership.objects.create(
            workspace=workspace_no_org,
            user=self.USER_WORKSPACE_EDITOR,
            role=WorkspaceMembershipRole.EDITOR,
        )

        # Organization admin/owner should not have permissions for workspace without organization
        self.assertFalse(
            view_database_credentials(self.USER_ORG_OWNER, workspace_no_org)
        )
        self.assertFalse(
            view_database_credentials(self.USER_ORG_ADMIN, workspace_no_org)
        )

        # Only workspace members with appropriate roles should have permissions
        self.assertTrue(
            view_database_credentials(self.USER_WORKSPACE_ADMIN, workspace_no_org)
        )
        self.assertTrue(
            view_database_credentials(self.USER_WORKSPACE_EDITOR, workspace_no_org)
        )
        self.assertFalse(
            view_database_credentials(self.USER_WORKSPACE_VIEWER, workspace_no_org)
        )
