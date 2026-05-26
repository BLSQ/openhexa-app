from django.test import TestCase

from hexa.datasets.models import Dataset
from hexa.pipeline_templates.models import PipelineTemplate
from hexa.pipelines.models import Pipeline
from hexa.user_management.models import (
    Membership,
    MembershipRole,
    Organization,
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
        # REAL_USER has access to BOTH workspaces. The whole point of this
        # test class is that WebappUser must scope down to just one.
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
        cls.WEBAPP_B = Webapp.objects.create(
            name="Webapp B",
            slug="webapp-b",
            subdomain="webapp-b",
            workspace=cls.WORKSPACE_B,
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
        self.assertTrue(self.webapp_user.is_service_principal)
        self.assertTrue(self.webapp_user.is_authenticated)

    def test_accessible_workspaces_only_includes_webapp_workspace(self):
        self.assertEqual(
            list(self.webapp_user.accessible_workspaces()), [self.WORKSPACE_A]
        )

    def test_webapps_scoped_to_webapp_workspace(self):
        webapps = Webapp.objects.filter_for_user(self.webapp_user)
        self.assertEqual(list(webapps), [self.WEBAPP_A])

    def test_pipelines_scoped_to_webapp_workspace(self):
        pipelines = Pipeline.objects.filter_for_user(self.webapp_user)
        # Pipeline B lives in workspace B; REAL_USER would normally see it.
        self.assertNotIn(self.PIPELINE_B, pipelines)

    def test_datasets_scoped_to_webapp_workspace(self):
        datasets = Dataset.objects.filter_for_user(self.webapp_user)
        self.assertNotIn(self.DATASET_B, datasets)

    def test_workspaces_scoped_to_webapp_workspace(self):
        workspaces = Workspace.objects.filter_for_user(self.webapp_user)
        self.assertEqual(list(workspaces), [self.WORKSPACE_A])

    def test_teams_short_circuit_to_empty(self):
        team = Team.objects.create(name="Some Team")
        Membership.objects.create(
            user=self.REAL_USER, team=team, role=MembershipRole.REGULAR
        )
        # The real user IS a member, but the webapp principal must not be
        # able to enumerate teams or memberships.
        self.assertEqual(Team.objects.filter_for_user(self.webapp_user).count(), 0)
        self.assertEqual(
            Membership.objects.filter_for_user(self.webapp_user).count(), 0
        )

    def test_workspace_memberships_short_circuit_to_empty(self):
        self.assertEqual(
            WorkspaceMembership.objects.filter_for_user(self.webapp_user).count(), 0
        )

    def test_workspace_invitations_short_circuit_to_empty(self):
        WorkspaceInvitation.objects.create(
            workspace=self.WORKSPACE_A,
            email="x@example.com",
            role=WorkspaceMembershipRole.VIEWER,
            invited_by=self.SUPERUSER,
        )
        self.assertEqual(
            WorkspaceInvitation.objects.filter_for_user(self.webapp_user).count(), 0
        )

    def test_pipeline_templates_visible_to_service_principal(self):
        # Templates are deliberately shared resources (matches PipelineRunUser).
        source = Pipeline.objects.create(
            name="Source", code="source", workspace=self.WORKSPACE_B
        )
        PipelineTemplate.objects.create(
            name="T",
            description="t",
            workspace=self.WORKSPACE_B,
            source_pipeline=source,
        )
        self.assertGreaterEqual(
            PipelineTemplate.objects.filter_for_user(self.webapp_user).count(), 1
        )

    def test_organizations_scoped_to_webapp_workspace_org(self):
        org = Organization.objects.create(
            name="Org", short_name="org", organization_type="CORPORATE"
        )
        self.WORKSPACE_A.organization = org
        self.WORKSPACE_A.save()
        orgs = Organization.objects.filter_for_user(self.webapp_user)
        self.assertEqual(list(orgs), [org])
