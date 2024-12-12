import uuid

from django.db.utils import IntegrityError

from hexa.core.test import TestCase
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.template_pipelines.models import Template, TemplateVersion
from hexa.workspaces.models import Workspace


class TemplateModelTest(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Test Workspace")
        self.other_workspace = Workspace.objects.create(name="Test Workspace2")
        self.pipeline = Pipeline.objects.create(
            name="Test Pipeline", workspace=self.workspace
        )

    def test_create_template(self):
        template = Template.objects.create(
            name="Test Template",
            code="test_code",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )
        self.assertIsInstance(template.id, uuid.UUID)
        self.assertEqual(template.name, "Test Template")
        self.assertEqual(template.code, "test_code")
        self.assertEqual(template.workspace, self.workspace)
        self.assertEqual(template.source_pipeline, self.pipeline)

    def test_unique_template_code_per_workspace(self):
        unique_code = "unique_code"
        Template.objects.create(
            name="Template 1",
            code=unique_code,
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )
        with self.assertRaises(IntegrityError):
            Template.objects.create(
                name="Template 2",
                code=unique_code,
                workspace=self.workspace,
                source_pipeline=self.pipeline,
            )

    def test_unique_template_name_across_all_workspaces(self):
        unique_name = "Unique Template"
        Template.objects.create(
            name=unique_name,
            code="code1",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )
        with self.assertRaises(IntegrityError):
            Template.objects.create(
                name=unique_name,
                code="code2",
                workspace=self.other_workspace,
                source_pipeline=self.pipeline,
            )


class TemplateVersionModelTest(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Test Workspace")
        self.pipeline = Pipeline.objects.create(
            name="Test Pipeline", workspace=self.workspace
        )
        self.pipeline_version = PipelineVersion.objects.create(
            pipeline=self.pipeline, version_number=1
        )
        self.template = Template.objects.create(
            name="Test Template",
            code="test_code",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )

    def test_create_template_version(self):
        template_version = TemplateVersion.objects.create(
            version_number=1,
            template=self.template,
            source_pipeline_version=self.pipeline_version,
        )
        self.assertIsInstance(template_version.id, uuid.UUID)
        self.assertEqual(template_version.version_number, 1)
        self.assertEqual(template_version.template, self.template)
        self.assertEqual(
            template_version.source_pipeline_version, self.pipeline_version
        )

    def test_unique_template_version_number(self):
        TemplateVersion.objects.create(
            version_number=1,
            template=self.template,
            source_pipeline_version=self.pipeline_version,
        )
        with self.assertRaises(IntegrityError):
            TemplateVersion.objects.create(
                version_number=1,
                template=self.template,
                source_pipeline_version=self.pipeline_version,
            )
