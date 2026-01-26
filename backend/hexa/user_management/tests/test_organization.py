from django.core.exceptions import PermissionDenied
from django.test import TestCase

from hexa.user_management.models import (
    Feature,
    FeatureFlag,
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.user_management.permissions import create_workspace
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class OrganizationModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="password"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="password"
        )
        self.user3 = User.objects.create_user(
            email="user3@example.com", password="password"
        )
        self.organization = Organization.objects.create(
            name="Test Organization",
            organization_type="CORPORATE",
        )
        self.membership = OrganizationMembership.objects.create(
            organization=self.organization,
            user=self.user1,
            role=OrganizationMembershipRole.ADMIN,
        )
        self.membership2 = OrganizationMembership.objects.create(
            organization=self.organization,
            user=self.user2,
            role=OrganizationMembershipRole.OWNER,
        )

    def test_organization_creation(self):
        self.assertEqual(self.organization.name, "Test Organization")
        self.assertEqual(self.organization.organization_type, "CORPORATE")

    def test_membership_creation(self):
        self.assertEqual(self.membership.organization, self.organization)
        self.assertEqual(self.membership.user, self.user1)
        self.assertEqual(self.membership.role, OrganizationMembershipRole.ADMIN)

    def test_filter_for_user(self):
        queryset = Organization.objects.filter_for_user(self.user1)
        self.assertIn(self.organization, queryset)

        queryset = Organization.objects.filter_for_user(self.user3)
        self.assertNotIn(self.organization, queryset)

    def test_filter_for_user_external_collaborator(self):
        workspace = Workspace.objects.create(
            name="Test Workspace",
            organization=self.organization,
        )
        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=self.user3,
            role=WorkspaceMembershipRole.VIEWER,
        )

        queryset = Organization.objects.filter_for_user(self.user3)
        self.assertIn(self.organization, queryset)

        queryset = Organization.objects.filter_for_user(
            self.user3, direct_membership_only=True
        )
        self.assertNotIn(self.organization, queryset)

    def test_update_own_membership_role(self):
        with self.assertRaises(PermissionDenied):
            self.membership.update_if_has_perm(
                principal=self.user1, role=OrganizationMembershipRole.ADMIN
            )

    def test_update_membership_role_as_owner(self):
        self.membership.update_if_has_perm(
            principal=self.user2, role=OrganizationMembershipRole.OWNER
        )
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.role, OrganizationMembershipRole.OWNER)

    def test_promoting_to_owner(self):
        """Test that a user cannot promote themselves to owner."""
        with self.assertRaises(PermissionDenied):
            self.membership.update_if_has_perm(
                principal=self.user1, role=OrganizationMembershipRole.OWNER
            )

    def test_delete_own_membership(self):
        """Test that a user cannot delete their own membership."""
        with self.assertRaises(PermissionDenied):
            self.membership.delete_if_has_perm(principal=self.user1)

    def test_delete_membership_without_permission(self):
        """Test that an admin cannot delete the membership of an owner of the organization."""
        with self.assertRaises(PermissionDenied):
            self.membership2.delete_if_has_perm(principal=self.user1)


class CreateWorkspacePermissionTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Test Workspace")
        self.admin = User.objects.create_user(
            email="user@example.com", password="password"
        )
        self.membership = WorkspaceMembership.objects.create(
            workspace=self.workspace,
            user=self.admin,
            role=WorkspaceMembershipRole.ADMIN,
        )

    def test_feature_flag_prevent_create_blocks_creation(self):
        feature = Feature.objects.create(code="workspaces.prevent_create")
        FeatureFlag.objects.create(feature=feature, user=self.admin)
        self.assertFalse(create_workspace(self.admin))

    def test_feature_flag_create_allows_creation(self):
        Organization.objects.create(name="Test Org")
        feature = Feature.objects.create(code="workspaces.create")
        FeatureFlag.objects.create(feature=feature, user=self.admin)
        self.membership.delete()

        self.assertTrue(create_workspace(self.admin))

    def test_legacy_mode_workspace_admin_can_create(self):
        self.assertTrue(create_workspace(self.admin))

    def test_legacy_mode_non_workspace_admin_cannot_create(self):
        self.membership.role = WorkspaceMembershipRole.EDITOR
        self.membership.save()
        self.assertFalse(create_workspace(self.admin))

    def test_with_organizations_no_org_param_denied(self):
        Organization.objects.create(name="Test Org")
        self.assertFalse(create_workspace(self.admin))

    def test_org_member_can_create_workspace(self):
        organization = Organization.objects.create(name="Test Org")
        for role in [
            OrganizationMembershipRole.MEMBER,
            OrganizationMembershipRole.ADMIN,
            OrganizationMembershipRole.OWNER,
        ]:
            with self.subTest(role=role):
                OrganizationMembership.objects.filter(user=self.admin).delete()
                OrganizationMembership.objects.create(
                    organization=organization, user=self.admin, role=role
                )
                self.assertTrue(create_workspace(self.admin, organization))

    def test_non_org_member_cannot_create(self):
        organization = Organization.objects.create(name="Test Org")
        self.assertFalse(create_workspace(self.admin, organization))
