from unittest.mock import MagicMock

from django.test import TestCase

from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import Pipeline, PipelineRun
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


class TestPipelineRunUserFiltering(TestCase):
    def setUp(self):
        self.USER_ROOT = User.objects.create_user(
            "root@bluesquarehub.com",
            "standardpassword",
            is_superuser=True,
        )
        self.WORKSPACE1 = Workspace.objects.create_if_has_perm(
            self.USER_ROOT,
            name="WS1",
            description="Workspace 1",
        )
        self.WORKSPACE2 = Workspace.objects.create_if_has_perm(
            self.USER_ROOT,
            name="WS2",
            description="Workspace 2",
        )
        self.pipeline_run = MagicMock(PipelineRun)
        self.pipeline_run.pipeline = MagicMock(Pipeline)
        self.pipeline_run.pipeline.workspace = self.WORKSPACE1
        self.pipeline_user = PipelineRunUser(self.pipeline_run)

    def test_pipeline_user_filtering(self):
        Pipeline.objects.create(
            name="Test Pipeline1",
            description="A test pipeline1",
            workspace=self.WORKSPACE1,
        )
        Pipeline.objects.create(
            name="Test Pipeline2",
            description="A test pipeline2",
            workspace=self.WORKSPACE2,
        )

        filtered_pipelines = Pipeline.objects.filter_for_user(self.pipeline_user)
        self.assertEqual(filtered_pipelines.count(), 1)
        self.assertEqual(filtered_pipelines.first().workspace, self.WORKSPACE1)

    def test_workspace_filtering(self):
        filtered_workspaces = Workspace.objects.filter_for_user(self.pipeline_user)
        self.assertEqual(filtered_workspaces.count(), 1)
        self.assertEqual(filtered_workspaces.first(), self.WORKSPACE1)

    def test_organization_filtering(self):
        from hexa.user_management.models import Organization

        org1 = Organization.objects.create(
            name="Org 1", short_name="org1", organization_type="CORPORATE"
        )
        Organization.objects.create(
            name="Org 2", short_name="org2", organization_type="ACADEMIC"
        )
        self.WORKSPACE1.organization = org1
        self.WORKSPACE1.save()

        filtered_orgs = Organization.objects.filter_for_user(self.pipeline_user)
        self.assertEqual(filtered_orgs.count(), 1)
        self.assertEqual(filtered_orgs.first(), org1)

    def test_dataset_filtering(self):
        from hexa.datasets.models import Dataset

        dataset1 = Dataset.objects.create_if_has_perm(
            principal=self.USER_ROOT,
            name="Dataset 1",
            description="Dataset 1",
            workspace=self.WORKSPACE1,
        )
        Dataset.objects.create_if_has_perm(
            principal=self.USER_ROOT,
            name="Dataset 2",
            description="Dataset 2",
            workspace=self.WORKSPACE2,
        )

        filtered_datasets = Dataset.objects.filter_for_user(self.pipeline_user)
        self.assertEqual(filtered_datasets.count(), 1)
        self.assertEqual(filtered_datasets.first(), dataset1)

    def test_webapp_filtering(self):
        from hexa.webapps.models import Webapp

        webapp1 = Webapp.objects.create(
            name="WebApp 1",
            slug="webapp-1",
            subdomain="webapp-1",
            workspace=self.WORKSPACE1,
            created_by=self.USER_ROOT,
        )
        Webapp.objects.create(
            name="WebApp 2",
            slug="webapp-2",
            subdomain="webapp-2",
            workspace=self.WORKSPACE2,
            created_by=self.USER_ROOT,
        )

        filtered_webapps = Webapp.objects.filter_for_user(self.pipeline_user)
        self.assertEqual(filtered_webapps.count(), 1)
        self.assertEqual(filtered_webapps.first(), webapp1)

    def test_pipeline_template_filtering(self):
        from hexa.pipeline_templates.models import PipelineTemplate

        source_pipeline1 = Pipeline.objects.create(
            name="Source Pipeline1",
            code="source_pipeline1_code",
            description="A source pipeline for template",
            workspace=self.WORKSPACE1,
        )

        source_pipeline2 = Pipeline.objects.create(
            name="Source Pipeline2",
            code="source_pipeline2_code",
            description="A source pipeline for template",
            workspace=self.WORKSPACE1,
        )

        PipelineTemplate.objects.create(
            name="Template 1",
            description="A test template 1",
            workspace=self.WORKSPACE1,
            source_pipeline=source_pipeline1,
        )
        PipelineTemplate.objects.create(
            name="Template 2",
            description="A test template 2",
            workspace=self.WORKSPACE2,
            source_pipeline=source_pipeline2,
        )

        filtered_templates = PipelineTemplate.objects.filter_for_user(
            self.pipeline_user
        )
        self.assertEqual(filtered_templates.count(), 2)  # Expect all templates


class TestPrincipalAccessors(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(
            "root@bluesquarehub.com", "standardpassword", is_superuser=True
        )
        self.member = User.objects.create_user(
            "member@bluesquarehub.com", "standardpassword"
        )
        self.outsider = User.objects.create_user(
            "outsider@bluesquarehub.com", "standardpassword"
        )
        self.workspace1 = Workspace.objects.create_if_has_perm(
            self.superuser, name="WS1", description="Workspace 1"
        )
        self.workspace2 = Workspace.objects.create_if_has_perm(
            self.superuser, name="WS2", description="Workspace 2"
        )
        WorkspaceMembership.objects.create(
            user=self.member,
            workspace=self.workspace1,
            role=WorkspaceMembershipRole.EDITOR,
        )
        self.pipeline_run = MagicMock(PipelineRun)
        self.pipeline_run.pipeline = MagicMock(Pipeline)
        self.pipeline_run.pipeline.workspace = self.workspace1
        self.pipeline_run.pipeline.workspace_id = self.workspace1.id
        self.pipeline_user = PipelineRunUser(self.pipeline_run)

    def test_user_accessible_workspaces_returns_memberships(self):
        accessible = self.member.accessible_workspaces()
        self.assertEqual(list(accessible), [self.workspace1])

    def test_user_accessible_workspaces_empty_for_outsider(self):
        self.assertEqual(self.outsider.accessible_workspaces().count(), 0)

    def test_user_accessible_workspaces_returns_all_for_superuser(self):
        self.assertEqual(
            set(self.superuser.accessible_workspaces()),
            {self.workspace1, self.workspace2},
        )

    def test_pipeline_user_accessible_workspaces_returns_pipeline_workspace(self):
        accessible = self.pipeline_user.accessible_workspaces()
        self.assertEqual(list(accessible), [self.workspace1])

    def test_user_accessible_workspaces_includes_org_admin_workspaces(self):
        # An organization admin/owner sees every workspace in the org,
        # including ones they have no direct WorkspaceMembership for.
        org_admin = User.objects.create_user(
            "org-admin@bluesquarehub.com", "standardpassword"
        )
        org = Organization.objects.create(
            name="Org", short_name="org", organization_type="CORPORATE"
        )
        OrganizationMembership.objects.create(
            user=org_admin,
            organization=org,
            role=OrganizationMembershipRole.ADMIN,
        )
        self.workspace1.organization = org
        self.workspace1.save()

        accessible = org_admin.accessible_workspaces()
        self.assertIn(self.workspace1, accessible)
        self.assertNotIn(self.workspace2, accessible)

    def test_user_accessible_workspaces_excludes_org_for_regular_members(self):
        # A REGULAR (non-admin/owner) organization member should NOT see
        # workspaces just because they share an org — only direct
        # WorkspaceMembership grants access.
        org_member = User.objects.create_user(
            "org-member@bluesquarehub.com", "standardpassword"
        )
        org = Organization.objects.create(
            name="Org", short_name="org", organization_type="CORPORATE"
        )
        OrganizationMembership.objects.create(
            user=org_member,
            organization=org,
            role=OrganizationMembershipRole.MEMBER,
        )
        self.workspace1.organization = org
        self.workspace1.save()

        self.assertEqual(org_member.accessible_workspaces().count(), 0)

    def test_user_accessible_organizations_includes_via_workspace(self):
        org = Organization.objects.create(
            name="Org", short_name="org", organization_type="CORPORATE"
        )
        self.workspace1.organization = org
        self.workspace1.save()
        self.assertEqual(list(self.member.accessible_organizations()), [org])

    def test_pipeline_user_accessible_organizations(self):
        org = Organization.objects.create(
            name="Org", short_name="org", organization_type="CORPORATE"
        )
        self.workspace1.organization = org
        self.workspace1.save()
        self.assertEqual(list(self.pipeline_user.accessible_organizations()), [org])

    def test_is_service_principal_flags(self):
        self.assertFalse(self.member.is_service_principal)
        self.assertFalse(self.superuser.is_service_principal)
        self.assertTrue(self.pipeline_user.is_service_principal)
