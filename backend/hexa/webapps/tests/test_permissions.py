from hexa.core.test import TestCase
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.webapps.models import Webapp
from hexa.webapps.permissions import (
    create_webapp,
    delete_webapp,
    share_webapp,
    update_webapp,
)
from hexa.workspaces.models import (
    WorkspaceMembership,
    WorkspaceMembershipRole,
)
from hexa.workspaces.tests.testutils import create_workspace


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

        cls.WORKSPACE = create_workspace(
            cls.USER_WORKSPACE_ADMIN,
            name="Test Workspace",
            description="Test workspace for webapps permissions",
            organization=cls.ORGANIZATION,
        )

        cls.USER_WORKSPACE_ADMIN.is_superuser = False
        cls.USER_WORKSPACE_ADMIN.save()
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_WORKSPACE_EDITOR,
            role=WorkspaceMembershipRole.EDITOR,
        )

        cls.WEBAPP = Webapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Test Webapp",
            slug="test-webapp",
            subdomain="test-webapp",
            created_by=cls.USER_WORKSPACE_ADMIN,
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


class ShareWebappPermissionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(
            name="Share Organization",
            short_name="share-org-webapps",
            organization_type="CORPORATE",
        )
        cls.ORG_ADMIN = User.objects.create_user("org_admin@share.com", "password")
        cls.ORG_MEMBER = User.objects.create_user("org_member@share.com", "password")
        cls.WS_ADMIN = User.objects.create_user(
            "ws_admin@share.com", "password", is_superuser=True
        )
        cls.AUTHOR = User.objects.create_user("author@share.com", "password")
        cls.EDITOR = User.objects.create_user("editor@share.com", "password")
        cls.VIEWER = User.objects.create_user("viewer@share.com", "password")
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_ADMIN,
            role=OrganizationMembershipRole.ADMIN,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_MEMBER,
            role=OrganizationMembershipRole.MEMBER,
        )
        cls.WORKSPACE = create_workspace(
            cls.WS_ADMIN, name="Share Workspace", organization=cls.ORGANIZATION
        )
        cls.WS_ADMIN.is_superuser = False
        cls.WS_ADMIN.save()
        for user, role in [
            (cls.AUTHOR, WorkspaceMembershipRole.EDITOR),
            (cls.EDITOR, WorkspaceMembershipRole.EDITOR),
            (cls.VIEWER, WorkspaceMembershipRole.VIEWER),
        ]:
            WorkspaceMembership.objects.create(
                workspace=cls.WORKSPACE, user=user, role=role
            )
        cls.WEBAPP = Webapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Shared Webapp",
            slug="shared-webapp",
            subdomain="shared-webapp",
            created_by=cls.AUTHOR,
        )

    def test_allowed(self):
        for user in [self.ORG_ADMIN, self.WS_ADMIN, self.AUTHOR]:
            with self.subTest(user=user.email):
                self.assertTrue(share_webapp(user, self.WEBAPP))

    def test_denied(self):
        for user in [self.EDITOR, self.VIEWER, self.ORG_MEMBER]:
            with self.subTest(user=user.email):
                self.assertFalse(share_webapp(user, self.WEBAPP))

    def test_author_demoted_to_viewer_is_denied(self):
        WorkspaceMembership.objects.filter(
            workspace=self.WORKSPACE, user=self.AUTHOR
        ).update(role=WorkspaceMembershipRole.VIEWER)
        self.assertFalse(share_webapp(self.AUTHOR, self.WEBAPP))
