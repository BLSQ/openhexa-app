from unittest.mock import MagicMock

from django.test import TestCase

from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import Pipeline, PipelineRun
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


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
            workspace=self.WORKSPACE1,
            created_by=self.USER_ROOT,
        )
        Webapp.objects.create(
            name="WebApp 2",
            slug="webapp-2",
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
