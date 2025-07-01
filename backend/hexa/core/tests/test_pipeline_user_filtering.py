from unittest.mock import MagicMock

from core.models.base import BaseQuerySet
from django.db.models import Q
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

    def test_not_implemented_error_for_models_without_workspace(self):
        class SomeModelQuerySet(BaseQuerySet):
            def filter_for_user(self, user):
                return self._filter_for_user_and_query_object(
                    user,
                    Q(organizationmembership__user=user),
                    return_all_if_superuser=True,
                )

        class SomeModel:
            objects = SomeModelQuerySet.as_manager()

        with self.assertRaises(NotImplementedError) as context:
            SomeModel.objects.filter_for_user(self.pipeline_user)
            self.assertIn(
                "Override _get_pipeline_run_user_workspace_query for SomeModel to allow pipeline run user access control",
                str(context.exception),
            )
