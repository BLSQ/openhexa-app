from hexa.core.test import TestCase
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.webapps.models import Webapp
from hexa.webapps.permissions import create_webapp, delete_webapp, update_webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WebappsOrganizationPermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-webapps",
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
            description="Test workspace for webapps permissions",
            organization=cls.ORGANIZATION,
        )

        cls.USER_WORKSPACE_ADMIN.is_superuser = False
        cls.USER_WORKSPACE_ADMIN.save()
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_WORKSPACE_ADMIN,
            role=WorkspaceMembershipRole.ADMIN,
        )
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_WORKSPACE_EDITOR,
            role=WorkspaceMembershipRole.EDITOR,
        )

        cls.WEBAPP = Webapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Test Webapp",
            description="Test webapp for permission testing",
            slug="test-webapp",
            config={"image": "test-image"},
        )

    def test_organization_owner_can_create_webapp(self):
        """Organization owners should be able to create webapps even without workspace membership"""
        self.assertTrue(create_webapp(self.USER_ORG_OWNER, self.WORKSPACE))

    def test_organization_admin_can_create_webapp(self):
        """Organization admins should be able to create webapps even without workspace membership"""
        self.assertTrue(create_webapp(self.USER_ORG_ADMIN, self.WORKSPACE))

    def test_organization_member_cannot_create_webapp(self):
        """Organization members should NOT be able to create webapps without workspace membership"""
        self.assertFalse(create_webapp(self.USER_ORG_MEMBER, self.WORKSPACE))

    def test_non_organization_member_cannot_create_webapp(self):
        """Non-organization members should NOT be able to create webapps without workspace membership"""
        self.assertFalse(create_webapp(self.USER_NON_ORG_MEMBER, self.WORKSPACE))

    def test_workspace_admin_can_create_webapp(self):
        """Workspace admins should be able to create webapps through workspace membership"""
        self.assertTrue(create_webapp(self.USER_WORKSPACE_ADMIN, self.WORKSPACE))

    def test_workspace_editor_can_create_webapp(self):
        """Workspace editors should be able to create webapps through workspace membership"""
        self.assertTrue(create_webapp(self.USER_WORKSPACE_EDITOR, self.WORKSPACE))

    def test_organization_owner_can_delete_webapp(self):
        """Organization owners should be able to delete webapps even without workspace membership"""
        self.assertTrue(delete_webapp(self.USER_ORG_OWNER, self.WEBAPP))

    def test_organization_admin_can_delete_webapp(self):
        """Organization admins should be able to delete webapps even without workspace membership"""
        self.assertTrue(delete_webapp(self.USER_ORG_ADMIN, self.WEBAPP))

    def test_organization_member_cannot_delete_webapp(self):
        """Organization members should NOT be able to delete webapps without workspace membership"""
        self.assertFalse(delete_webapp(self.USER_ORG_MEMBER, self.WEBAPP))

    def test_non_organization_member_cannot_delete_webapp(self):
        """Non-organization members should NOT be able to delete webapps without workspace membership"""
        self.assertFalse(delete_webapp(self.USER_NON_ORG_MEMBER, self.WEBAPP))

    def test_workspace_admin_can_delete_webapp(self):
        """Workspace admins should be able to delete webapps through workspace membership"""
        self.assertTrue(delete_webapp(self.USER_WORKSPACE_ADMIN, self.WEBAPP))

    def test_workspace_editor_cannot_delete_webapp(self):
        """Workspace editors should NOT be able to delete webapps (only admins can delete)"""
        self.assertFalse(delete_webapp(self.USER_WORKSPACE_EDITOR, self.WEBAPP))

    def test_organization_owner_can_update_webapp(self):
        """Organization owners should be able to update webapps even without workspace membership"""
        self.assertTrue(update_webapp(self.USER_ORG_OWNER, self.WEBAPP))

    def test_organization_admin_can_update_webapp(self):
        """Organization admins should be able to update webapps even without workspace membership"""
        self.assertTrue(update_webapp(self.USER_ORG_ADMIN, self.WEBAPP))

    def test_organization_member_cannot_update_webapp(self):
        """Organization members should NOT be able to update webapps without workspace membership"""
        self.assertFalse(update_webapp(self.USER_ORG_MEMBER, self.WEBAPP))

    def test_non_organization_member_cannot_update_webapp(self):
        """Non-organization members should NOT be able to update webapps without workspace membership"""
        self.assertFalse(update_webapp(self.USER_NON_ORG_MEMBER, self.WEBAPP))

    def test_workspace_admin_can_update_webapp(self):
        """Workspace admins should be able to update webapps through workspace membership"""
        self.assertTrue(update_webapp(self.USER_WORKSPACE_ADMIN, self.WEBAPP))

    def test_workspace_editor_can_update_webapp(self):
        """Workspace editors should be able to update webapps through workspace membership"""
        self.assertTrue(update_webapp(self.USER_WORKSPACE_EDITOR, self.WEBAPP))

    def test_permissions_with_null_organization(self):
        """Test permissions when workspace has no organization"""
        workspace_no_org = Workspace.objects.create_if_has_perm(
            self.USER_WORKSPACE_ADMIN,
            name="No Org Workspace",
            description="Workspace without organization",
            organization=None,
        )

        webapp_no_org = Webapp.objects.create(
            workspace=workspace_no_org,
            name="Test Webapp No Org",
            description="Test webapp in workspace without organization",
            slug="test-webapp-no-org",
            config={"image": "test-image"},
        )

        # Organization admin/owner should not have permissions for webapp in workspace without organization
        self.assertFalse(create_webapp(self.USER_ORG_OWNER, workspace_no_org))
        self.assertFalse(create_webapp(self.USER_ORG_ADMIN, workspace_no_org))
        self.assertFalse(delete_webapp(self.USER_ORG_OWNER, webapp_no_org))
        self.assertFalse(delete_webapp(self.USER_ORG_ADMIN, webapp_no_org))
        self.assertFalse(update_webapp(self.USER_ORG_OWNER, webapp_no_org))
        self.assertFalse(update_webapp(self.USER_ORG_ADMIN, webapp_no_org))

        # Only workspace member should have permissions
        self.assertTrue(create_webapp(self.USER_WORKSPACE_ADMIN, workspace_no_org))
        self.assertTrue(delete_webapp(self.USER_WORKSPACE_ADMIN, webapp_no_org))
        self.assertTrue(update_webapp(self.USER_WORKSPACE_ADMIN, webapp_no_org))
