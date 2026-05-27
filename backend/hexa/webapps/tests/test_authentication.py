from unittest.mock import patch

from django.test import TestCase

from hexa.datasets.models import Dataset
from hexa.pipelines.models import Pipeline
from hexa.user_management.models import (
    Membership,
    MembershipRole,
    Organization,
    ServicePrincipal,
    Team,
    User,
)
from hexa.webapps.authentication import WebappUser
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceInvitation,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class TestWebappUserFiltering(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.SUPERUSER = User.objects.create_user(
            "root@bluesquarehub.com", "password", is_superuser=True
        )
        cls.REAL_USER = User.objects.create_user("embed@bluesquarehub.com", "password")
        cls.WORKSPACE_A = Workspace.objects.create_if_has_perm(
            cls.SUPERUSER, name="Workspace A"
        )
        cls.WORKSPACE_B = Workspace.objects.create_if_has_perm(
            cls.SUPERUSER, name="Workspace B"
        )
        WorkspaceMembership.objects.create(
            user=cls.REAL_USER,
            workspace=cls.WORKSPACE_A,
            role=WorkspaceMembershipRole.EDITOR,
        )
        WorkspaceMembership.objects.create(
            user=cls.REAL_USER,
            workspace=cls.WORKSPACE_B,
            role=WorkspaceMembershipRole.EDITOR,
        )

        cls.WEBAPP_A = Webapp.objects.create(
            name="Webapp A",
            slug="webapp-a",
            subdomain="webapp-a",
            workspace=cls.WORKSPACE_A,
            created_by=cls.SUPERUSER,
        )
        cls.PIPELINE_B = Pipeline.objects.create(
            name="Pipeline B", workspace=cls.WORKSPACE_B
        )
        cls.DATASET_B = Dataset.objects.create_if_has_perm(
            principal=cls.SUPERUSER,
            workspace=cls.WORKSPACE_B,
            name="Dataset B",
            description="",
        )

        cls.webapp_user = WebappUser(real_user=cls.REAL_USER, webapp=cls.WEBAPP_A)

    def test_is_service_principal(self):
        self.assertIsInstance(self.webapp_user, ServicePrincipal)

    def test_is_active_delegates_to_real_user(self):
        self.REAL_USER.is_active = True
        self.assertTrue(self.webapp_user.is_active)
        self.REAL_USER.is_active = False
        self.assertFalse(self.webapp_user.is_active)

    def test_is_authenticated_delegates_to_real_user(self):
        self.assertTrue(self.webapp_user.is_authenticated)

    def test_has_perm_delegates_to_real_user(self):
        with patch.object(
            self.REAL_USER, "has_perm", return_value="DELEGATED"
        ) as mock_has_perm:
            result = self.webapp_user.has_perm("some.perm", self.WORKSPACE_A)

        mock_has_perm.assert_called_once_with("some.perm", self.WORKSPACE_A)
        self.assertEqual(result, "DELEGATED")

    def test_has_feature_flag_delegates_to_real_user(self):
        with patch.object(
            self.REAL_USER, "has_feature_flag", return_value="DELEGATED"
        ) as mock_flag:
            result = self.webapp_user.has_feature_flag("some_flag")

        mock_flag.assert_called_once_with("some_flag")
        self.assertEqual(result, "DELEGATED")

    def test_real_user_accessor_returns_embedding_user(self):
        self.assertEqual(self.webapp_user.real_user, self.REAL_USER)

    def test_workspaces_scoped_to_webapp_workspace(self):
        workspaces = Workspace.objects.filter_for_user(self.webapp_user)
        self.assertEqual(list(workspaces), [self.WORKSPACE_A])

    def test_pipelines_scoped_to_webapp_workspace(self):
        pipelines = Pipeline.objects.filter_for_user(self.webapp_user)
        self.assertNotIn(self.PIPELINE_B, pipelines)

    def test_datasets_scoped_to_webapp_workspace(self):
        datasets = Dataset.objects.filter_for_user(self.webapp_user)
        self.assertNotIn(self.DATASET_B, datasets)

    def test_teams_short_circuit_to_empty(self):
        team = Team.objects.create(name="Some Team")
        Membership.objects.create(
            user=self.REAL_USER, team=team, role=MembershipRole.REGULAR
        )
        self.assertEqual(Team.objects.filter_for_user(self.webapp_user).count(), 0)
        self.assertEqual(
            Membership.objects.filter_for_user(self.webapp_user).count(), 0
        )

    def test_workspace_memberships_scoped_to_webapp_workspace(self):
        memberships = WorkspaceMembership.objects.filter_for_user(self.webapp_user)
        seen_workspaces = {m.workspace_id for m in memberships}
        self.assertEqual(seen_workspaces, {self.WORKSPACE_A.id})

    def test_workspace_invitations_scoped_to_webapp_workspace(self):
        WorkspaceInvitation.objects.create(
            workspace=self.WORKSPACE_A,
            email="a@example.com",
            role=WorkspaceMembershipRole.VIEWER,
            invited_by=self.SUPERUSER,
        )
        WorkspaceInvitation.objects.create(
            workspace=self.WORKSPACE_B,
            email="b@example.com",
            role=WorkspaceMembershipRole.VIEWER,
            invited_by=self.SUPERUSER,
        )
        invitations = WorkspaceInvitation.objects.filter_for_user(self.webapp_user)
        seen_workspaces = {i.workspace_id for i in invitations}
        self.assertEqual(seen_workspaces, {self.WORKSPACE_A.id})

    def test_organizations_scoped_to_webapp_workspace_org(self):
        org = Organization.objects.create(
            name="Org", short_name="org", organization_type="CORPORATE"
        )
        self.WORKSPACE_A.organization = org
        self.WORKSPACE_A.save()
        self.assertEqual(
            list(Organization.objects.filter_for_user(self.webapp_user)), [org]
        )
