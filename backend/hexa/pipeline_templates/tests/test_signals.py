from unittest.mock import patch

from django.test import TestCase

from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import (
    Workspace,
)


class AutoUpdatePipelineSignalTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.organization = Organization.objects.create(name="Test Organization")
        cls.user = User.objects.create_user(
            "testuser@example.com", "password", first_name="Test", last_name="User"
        )
        OrganizationMembership.objects.create(
            organization=cls.organization,
            user=cls.user,
            role=OrganizationMembershipRole.ADMIN,
        )

    def setUp(self):
        # Create workspace with auto-update enabled
        self.workspace_auto = Workspace.objects.create_if_has_perm(
            principal=self.user,
            name="Auto-Update Workspace",
            description="Workspace with auto-update enabled",
            auto_update_pipelines_from_template=True,
            organization=self.organization,
        )

        # Create workspace with auto-update disabled
        self.workspace_manual = Workspace.objects.create_if_has_perm(
            principal=self.user,
            name="Manual Update Workspace",
            description="Workspace with auto-update disabled",
            auto_update_pipelines_from_template=False,
            organization=self.organization,
        )

        # Create a source pipeline
        self.source_pipeline = Pipeline.objects.create(
            name="Source Pipeline",
            code="source-pipeline",
            workspace=self.workspace_auto,
        )

        # Create initial pipeline version
        self.initial_version = PipelineVersion.objects.create(
            user=self.user,
            pipeline=self.source_pipeline,
            name="Initial Version",
            zipfile=b"initial zipfile content",
            parameters=[
                {
                    "code": "param1",
                    "name": "Parameter 1",
                    "type": "str",
                    "default": "default",
                }
            ],
            config={"param1": "initial_value"},
        )

        # Create template from source pipeline
        self.template = PipelineTemplate.objects.create(
            name="Test Template",
            code="test-template",
            description="A test template",
            workspace=self.workspace_auto,
            source_pipeline=self.source_pipeline,
        )

        # Create initial template version
        self.template_version_1 = PipelineTemplateVersion.objects.create(
            template=self.template,
            version_number=1,
            user=self.user,
            changelog="Initial template version",
            source_pipeline_version=self.initial_version,
        )

        # Create pipelines from template
        self.pipeline_auto = Pipeline.objects.create(
            name="Auto Update Pipeline",
            code="auto-update-pipeline",
            source_template=self.template,
            workspace=self.workspace_auto,
        )

        self.pipeline_manual = Pipeline.objects.create(
            name="Manual Update Pipeline",
            code="manual-update-pipeline",
            source_template=self.template,
            workspace=self.workspace_manual,
        )

        # Create pipeline versions from template
        self.pipeline_version_auto = self.template_version_1.create_pipeline_version(
            self.user, self.workspace_auto, self.pipeline_auto
        )

        self.pipeline_version_manual = self.template_version_1.create_pipeline_version(
            self.user, self.workspace_manual, self.pipeline_manual
        )

    def test_auto_update_signal_enabled_workspace(self):
        """Test that pipelines are auto-updated in workspaces with auto-update enabled"""
        # Record initial version counts
        initial_auto_versions = self.pipeline_auto.versions.count()
        initial_manual_versions = self.pipeline_manual.versions.count()

        # Create new pipeline version for source
        new_source_version = PipelineVersion.objects.create(
            user=self.user,
            pipeline=self.source_pipeline,
            name="Updated Version",
            zipfile=b"updated zipfile content",
            parameters=[
                {
                    "code": "param1",
                    "name": "Parameter 1",
                    "type": "str",
                    "default": "updated",
                }
            ],
            config={"param1": "updated_value"},
        )

        # Create new template version (this should trigger the signal)
        new_template_version = PipelineTemplateVersion.objects.create(
            template=self.template,
            version_number=2,
            user=self.user,
            changelog="Updated template version",
            source_pipeline_version=new_source_version,
        )

        # Refresh from database
        self.pipeline_auto.refresh_from_db()
        self.pipeline_manual.refresh_from_db()

        # Check that auto-update workspace pipeline was updated
        self.assertEqual(self.pipeline_auto.versions.count(), initial_auto_versions + 1)
        latest_auto_version = self.pipeline_auto.versions.first()
        self.assertEqual(
            latest_auto_version.source_template_version, new_template_version
        )

        # Check that manual-update workspace pipeline was NOT updated
        self.assertEqual(self.pipeline_manual.versions.count(), initial_manual_versions)

    def test_auto_update_signal_disabled_workspace(self):
        """Test that pipelines are not auto-updated in workspaces with auto-update disabled"""
        # Disable auto-update for the auto workspace to test the negative case
        self.workspace_auto.auto_update_pipelines_from_template = False
        self.workspace_auto.save()

        initial_versions = self.pipeline_auto.versions.count()

        # Create new pipeline version and template version
        new_source_version = PipelineVersion.objects.create(
            user=self.user,
            pipeline=self.source_pipeline,
            name="Another Update",
            zipfile=b"another update content",
            parameters=[{"code": "param1", "name": "Parameter 1", "type": "str"}],
        )

        PipelineTemplateVersion.objects.create(
            template=self.template,
            version_number=2,
            user=self.user,
            changelog="Another update",
            source_pipeline_version=new_source_version,
        )

        # Check that no new versions were created
        self.pipeline_auto.refresh_from_db()
        self.assertEqual(self.pipeline_auto.versions.count(), initial_versions)

    @patch("hexa.pipeline_templates.signals.logger")
    def test_auto_update_signal_logging(self, mock_logger):
        """Test that the signal logs appropriate messages"""
        # Create new template version
        new_source_version = PipelineVersion.objects.create(
            user=self.user,
            pipeline=self.source_pipeline,
            name="Logging Test Version",
            zipfile=b"logging test content",
            parameters=[{"code": "param1", "name": "Parameter 1", "type": "str"}],
        )

        PipelineTemplateVersion.objects.create(
            template=self.template,
            version_number=2,
            user=self.user,
            changelog="Logging test",
            source_pipeline_version=new_source_version,
        )

        # Verify logging calls
        mock_logger.info.assert_called()
        log_calls = [call.args[0] for call in mock_logger.info.call_args_list]

        # Check that we logged the template version creation and successful update
        self.assertTrue(
            any("New template version created" in call for call in log_calls)
        )
        self.assertTrue(any("Successfully auto-updated" in call for call in log_calls))

    def test_auto_update_signal_no_user(self):
        """Test that signal handles template versions without a user gracefully"""
        initial_versions = self.pipeline_auto.versions.count()

        # Create new pipeline version
        new_source_version = PipelineVersion.objects.create(
            user=self.user,
            pipeline=self.source_pipeline,
            name="No User Version",
            zipfile=b"no user content",
            parameters=[{"code": "param1", "name": "Parameter 1", "type": "str"}],
        )

        # Create template version without user (should not trigger auto-update)
        PipelineTemplateVersion.objects.create(
            template=self.template,
            version_number=2,
            user=None,  # No user
            changelog="No user test",
            source_pipeline_version=new_source_version,
        )

        # Check that no new versions were created
        self.pipeline_auto.refresh_from_db()
        self.assertEqual(self.pipeline_auto.versions.count(), initial_versions)
