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
        self.workspace_auto = Workspace.objects.create_if_has_perm(
            principal=self.user,
            name="Auto-Update Workspace",
            description="Workspace with auto-update enabled",
            auto_update_pipelines_from_template=True,
            organization=self.organization,
        )

        self.workspace_manual = Workspace.objects.create_if_has_perm(
            principal=self.user,
            name="Manual Update Workspace",
            description="Workspace with auto-update disabled",
            auto_update_pipelines_from_template=False,
            organization=self.organization,
        )

        self.source_pipeline = Pipeline.objects.create(
            name="Source Pipeline",
            code="source-pipeline",
            workspace=self.workspace_auto,
        )

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

        self.template = PipelineTemplate.objects.create(
            name="Test Template",
            code="test-template",
            description="A test template",
            workspace=self.workspace_auto,
            source_pipeline=self.source_pipeline,
        )

        self.template_version_1 = PipelineTemplateVersion.objects.create(
            template=self.template,
            version_number=1,
            user=self.user,
            changelog="Initial template version",
            source_pipeline_version=self.initial_version,
        )

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

        self.pipeline_version_auto = self.template_version_1.create_pipeline_version(
            self.user, self.workspace_auto, self.pipeline_auto
        )

        self.pipeline_version_manual = self.template_version_1.create_pipeline_version(
            self.user, self.workspace_manual, self.pipeline_manual
        )

    def test_auto_update_signal_enabled_workspace(self):
        """Test that pipelines are auto-updated in workspaces with auto-update enabled"""
        initial_auto_versions = self.pipeline_auto.versions.count()
        initial_manual_versions = self.pipeline_manual.versions.count()

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

        new_template_version = PipelineTemplateVersion.objects.create(
            template=self.template,
            version_number=2,
            user=self.user,
            changelog="Updated template version",
            source_pipeline_version=new_source_version,
        )

        self.pipeline_auto.refresh_from_db()
        self.pipeline_manual.refresh_from_db()

        self.assertEqual(self.pipeline_auto.versions.count(), initial_auto_versions + 1)
        latest_auto_version = self.pipeline_auto.versions.first()
        self.assertEqual(
            latest_auto_version.source_template_version, new_template_version
        )

        self.assertEqual(self.pipeline_manual.versions.count(), initial_manual_versions)

    def test_auto_update_signal_disabled_workspace(self):
        """Test that pipelines are not auto-updated in workspaces with auto-update disabled"""
        self.workspace_auto.auto_update_pipelines_from_template = False
        self.workspace_auto.save()

        initial_versions = self.pipeline_auto.versions.count()

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

        self.pipeline_auto.refresh_from_db()
        self.assertEqual(self.pipeline_auto.versions.count(), initial_versions)

    @patch("hexa.pipeline_templates.signals.logger")
    def test_auto_update_signal_logging(self, mock_logger):
        """Test that the signal logs appropriate messages"""
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

        mock_logger.info.assert_called()
        log_calls = [call.args[0] for call in mock_logger.info.call_args_list]

        self.assertTrue(
            any("New template version created" in call for call in log_calls)
        )
        self.assertTrue(any("Successfully auto-updated" in call for call in log_calls))

    def test_auto_update_signal_no_user_fallback(self):
        """Test that signal uses workspace creator when template version has no user"""
        initial_versions = self.pipeline_auto.versions.count()

        new_source_version = PipelineVersion.objects.create(
            user=self.user,
            pipeline=self.source_pipeline,
            name="No User Version",
            zipfile=b"no user content",
            parameters=[{"code": "param1", "name": "Parameter 1", "type": "str"}],
        )

        new_template_version = PipelineTemplateVersion.objects.create(
            template=self.template,
            version_number=2,
            user=None,
            changelog="CI/CD generated version",
            source_pipeline_version=new_source_version,
        )

        self.pipeline_auto.refresh_from_db()
        self.assertEqual(self.pipeline_auto.versions.count(), initial_versions + 1)
        latest_version = self.pipeline_auto.versions.first()
        self.assertEqual(latest_version.source_template_version, new_template_version)

    def test_auto_update_signal_no_principal_available(self):
        """Test that signal is skipped when no principal is available"""
        initial_versions = self.pipeline_auto.versions.count()

        self.workspace_auto.created_by = None
        self.workspace_auto.save()

        new_source_version = PipelineVersion.objects.create(
            user=self.user,
            pipeline=self.source_pipeline,
            name="No Principal Version",
            zipfile=b"no principal content",
            parameters=[{"code": "param1", "name": "Parameter 1", "type": "str"}],
        )

        PipelineTemplateVersion.objects.create(
            template=self.template,
            version_number=2,
            user=None,
            changelog="No principal available",
            source_pipeline_version=new_source_version,
        )

        self.pipeline_auto.refresh_from_db()
        self.assertEqual(self.pipeline_auto.versions.count(), initial_versions)
