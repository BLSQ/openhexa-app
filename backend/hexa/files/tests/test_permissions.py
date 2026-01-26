from hexa.core.test import TestCase
from hexa.files.permissions import create_object, delete_object
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


class FilesOrganizationPermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-files",
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
            description="Test workspace for files permissions",
            organization=cls.ORGANIZATION,
        )

        cls.USER_WORKSPACE_ADMIN.is_superuser = False
        cls.USER_WORKSPACE_ADMIN.save()

    def test_organization_owner_can_create_object(self):
        """Organization owners should be able to create files in workspace even without workspace membership"""
        self.assertTrue(create_object(self.USER_ORG_OWNER, self.WORKSPACE))

    def test_organization_admin_can_create_object(self):
        """Organization admins should be able to create files in workspace even without workspace membership"""
        self.assertTrue(create_object(self.USER_ORG_ADMIN, self.WORKSPACE))

    def test_organization_member_cannot_create_object(self):
        """Organization members should NOT be able to create files without workspace membership"""
        self.assertFalse(create_object(self.USER_ORG_MEMBER, self.WORKSPACE))

    def test_non_organization_member_cannot_create_object(self):
        """Non-organization members should NOT be able to create files without workspace membership"""
        self.assertFalse(create_object(self.USER_NON_ORG_MEMBER, self.WORKSPACE))

    def test_workspace_admin_can_create_object(self):
        """Workspace admins should be able to create files through workspace membership"""
        self.assertTrue(create_object(self.USER_WORKSPACE_ADMIN, self.WORKSPACE))

    def test_organization_owner_can_delete_object(self):
        """Organization owners should be able to delete files in workspace even without workspace membership"""
        self.assertTrue(delete_object(self.USER_ORG_OWNER, self.WORKSPACE))

    def test_organization_admin_can_delete_object(self):
        """Organization admins should be able to delete files in workspace even without workspace membership"""
        self.assertTrue(delete_object(self.USER_ORG_ADMIN, self.WORKSPACE))

    def test_organization_member_cannot_delete_object(self):
        """Organization members should NOT be able to delete files without workspace membership"""
        self.assertFalse(delete_object(self.USER_ORG_MEMBER, self.WORKSPACE))

    def test_non_organization_member_cannot_delete_object(self):
        """Non-organization members should NOT be able to delete files without workspace membership"""
        self.assertFalse(delete_object(self.USER_NON_ORG_MEMBER, self.WORKSPACE))

    def test_workspace_admin_can_delete_object(self):
        """Workspace admins should be able to delete files through workspace membership"""
        self.assertTrue(delete_object(self.USER_WORKSPACE_ADMIN, self.WORKSPACE))

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

        # Organization admin/owner should not have permissions for workspace without organization
        self.assertFalse(create_object(self.USER_ORG_OWNER, workspace_no_org))
        self.assertFalse(create_object(self.USER_ORG_ADMIN, workspace_no_org))
        self.assertFalse(delete_object(self.USER_ORG_OWNER, workspace_no_org))
        self.assertFalse(delete_object(self.USER_ORG_ADMIN, workspace_no_org))

        # Only workspace member should have permissions
        self.assertTrue(create_object(self.USER_WORKSPACE_ADMIN, workspace_no_org))
        self.assertTrue(delete_object(self.USER_WORKSPACE_ADMIN, workspace_no_org))
