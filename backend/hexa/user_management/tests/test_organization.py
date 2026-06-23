from unittest.mock import MagicMock, patch

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import Pipeline, PipelineRun
from hexa.user_management.models import (
    Feature,
    FeatureFlag,
    Organization,
    OrganizationInvitation,
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

    def test_slug_auto_generated_from_name(self):
        org = Organization.objects.create(name="My New Org")
        self.assertEqual(org.slug, "my-new-org")

    def test_slug_immutable_on_name_change(self):
        org = Organization.objects.create(name="Original Name")
        original_slug = org.slug
        org.name = "Updated Name"
        org.save()
        org.refresh_from_db()
        self.assertEqual(org.slug, original_slug)

    def test_slug_unique_on_collision(self):
        org1 = Organization.objects.create(name="Duplicate Org")
        org1.name = "Something Else"
        org1.save()
        org2 = Organization.objects.create(name="Duplicate Org")
        self.assertEqual(org1.slug, "duplicate-org")
        self.assertNotEqual(org2.slug, org1.slug)
        self.assertTrue(org2.slug.startswith("duplicate-org"))

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

    def test_invitations_not_visible_to_external_collaborator(self):
        """A workspace member who is not a direct organization member must not
        see the organization's invitations.
        """
        workspace = Workspace.objects.create(
            name="Test Workspace",
            organization=self.organization,
        )
        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=self.user3,
            role=WorkspaceMembershipRole.VIEWER,
        )
        invitation = OrganizationInvitation.objects.create(
            organization=self.organization,
            email="invitee@example.com",
            role=OrganizationMembershipRole.MEMBER,
            invited_by=self.user1,
        )

        self.assertIn(
            invitation,
            OrganizationInvitation.objects.filter_for_user(self.user1),
        )
        self.assertNotIn(
            invitation,
            OrganizationInvitation.objects.filter_for_user(self.user3),
        )

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


class OrganizationFilterForUserDispatchTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_user(
            "root@example.com", "password", is_superuser=True
        )
        cls.org_owner = User.objects.create_user("owner@example.com", "password")
        cls.org_admin = User.objects.create_user("orgadmin@example.com", "password")
        cls.org_member = User.objects.create_user("orgmember@example.com", "password")
        cls.workspace_only_user = User.objects.create_user(
            "wsonly@example.com", "password"
        )
        cls.external = User.objects.create_user("external@example.com", "password")

        cls.org = Organization.objects.create(name="Org A")
        cls.other_org = Organization.objects.create(name="Org B")
        OrganizationMembership.objects.create(
            organization=cls.org,
            user=cls.org_owner,
            role=OrganizationMembershipRole.OWNER,
        )
        OrganizationMembership.objects.create(
            organization=cls.org,
            user=cls.org_admin,
            role=OrganizationMembershipRole.ADMIN,
        )
        OrganizationMembership.objects.create(
            organization=cls.org,
            user=cls.org_member,
            role=OrganizationMembershipRole.MEMBER,
        )

        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            cls.org_workspace = Workspace.objects.create_if_has_perm(
                principal=cls.superuser,
                name="Org Workspace",
                organization=cls.org,
            )
            cls.standalone_workspace = Workspace.objects.create_if_has_perm(
                principal=cls.superuser, name="Standalone WS"
            )
            cls.other_org_workspace = Workspace.objects.create_if_has_perm(
                principal=cls.superuser,
                name="Other Org WS",
                organization=cls.other_org,
            )
        WorkspaceMembership.objects.create(
            workspace=cls.org_workspace,
            user=cls.workspace_only_user,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def test_anonymous_user_sees_nothing(self):
        self.assertEqual(
            Organization.objects.filter_for_user(AnonymousUser()).count(), 0
        )

    def test_anonymous_user_with_direct_membership_only_sees_nothing(self):
        self.assertEqual(
            Organization.objects.filter_for_user(
                AnonymousUser(), direct_membership_only=True
            ).count(),
            0,
        )

    def test_superuser_sees_all(self):
        result = set(Organization.objects.filter_for_user(self.superuser))
        self.assertEqual(result, {self.org, self.other_org})

    def test_org_owner_sees_their_org(self):
        self.assertIn(self.org, Organization.objects.filter_for_user(self.org_owner))
        self.assertNotIn(
            self.other_org, Organization.objects.filter_for_user(self.org_owner)
        )

    def test_org_member_sees_their_org(self):
        self.assertIn(self.org, Organization.objects.filter_for_user(self.org_member))

    def test_workspace_only_user_sees_org_via_workspace(self):
        self.assertIn(
            self.org,
            Organization.objects.filter_for_user(self.workspace_only_user),
        )

    def test_direct_membership_only_excludes_workspace_path(self):
        self.assertNotIn(
            self.org,
            Organization.objects.filter_for_user(
                self.workspace_only_user, direct_membership_only=True
            ),
        )

    def test_direct_membership_only_keeps_direct_members(self):
        self.assertIn(
            self.org,
            Organization.objects.filter_for_user(
                self.org_member, direct_membership_only=True
            ),
        )

    def test_external_user_sees_nothing(self):
        self.assertEqual(Organization.objects.filter_for_user(self.external).count(), 0)

    def test_pipeline_run_user_sees_orgs_of_its_workspace(self):
        pipeline_run = MagicMock(PipelineRun)
        pipeline_run.pipeline = MagicMock(Pipeline)
        pipeline_run.pipeline.workspace_id = self.org_workspace.id
        principal = PipelineRunUser(pipeline_run)

        result = list(Organization.objects.filter_for_user(principal))
        self.assertEqual(result, [self.org])

    def test_pipeline_run_user_in_standalone_workspace_sees_no_orgs(self):
        pipeline_run = MagicMock(PipelineRun)
        pipeline_run.pipeline = MagicMock(Pipeline)
        pipeline_run.pipeline.workspace_id = self.standalone_workspace.id
        principal = PipelineRunUser(pipeline_run)

        self.assertEqual(Organization.objects.filter_for_user(principal).count(), 0)

    def test_pipeline_run_user_ignores_direct_membership_only_flag(self):
        pipeline_run = MagicMock(PipelineRun)
        pipeline_run.pipeline = MagicMock(Pipeline)
        pipeline_run.pipeline.workspace_id = self.org_workspace.id
        principal = PipelineRunUser(pipeline_run)

        self.assertEqual(
            list(
                Organization.objects.filter_for_user(
                    principal, direct_membership_only=True
                )
            ),
            [self.org],
        )


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


class OrganizationGitLifecycleTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="gituser@example.com", password="password"
        )
        self.organization = Organization.objects.create(
            name="Git Test Org",
            organization_type="CORPORATE",
        )

    @patch("hexa.user_management.models.get_forgejo_client")
    def test_archive_git_org_on_delete(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.list_org_repositories.return_value = [
            {"name": "repo-1", "archived": False},
            {"name": "repo-2", "archived": False},
        ]

        self.organization.delete()

        org_slug = self.organization.slug
        mock_client.list_org_repositories.assert_called_once_with(org_slug)
        self.assertEqual(mock_client.archive_repository.call_count, 2)
        mock_client.archive_repository.assert_any_call(org_slug, "repo-1")
        mock_client.archive_repository.assert_any_call(org_slug, "repo-2")

    @patch("hexa.user_management.models.get_forgejo_client")
    def test_unarchive_git_org_on_restore(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.list_org_repositories.return_value = [
            {"name": "repo-1", "archived": True},
            {"name": "repo-2", "archived": False},
        ]

        self.organization.delete()
        mock_client.reset_mock()
        mock_client.list_org_repositories.return_value = [
            {"name": "repo-1", "archived": True},
            {"name": "repo-2", "archived": False},
        ]

        self.organization.restore()

        org_slug = self.organization.slug
        mock_client.list_org_repositories.assert_called_once_with(org_slug)
        mock_client.unarchive_repository.assert_called_once_with(org_slug, "repo-1")
