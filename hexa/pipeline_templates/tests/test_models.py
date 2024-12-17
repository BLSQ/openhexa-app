from django.db.utils import IntegrityError

from hexa.core.test import TestCase
from hexa.pipeline_templates.models import Template, TemplateVersion
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.workspaces.models import Workspace


class TemplateModelTest(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(
            name="Test Workspace", slug="test-workspace", db_name="test_workspace"
        )
        self.other_workspace = Workspace.objects.create(
            name="Test Workspace2", slug="test-workspace2", db_name="test_workspace2"
        )
        self.pipeline = Pipeline.objects.create(
            name="Test Pipeline", workspace=self.workspace
        )
        self.pipeline_version1 = PipelineVersion.objects.create(
            pipeline=self.pipeline, version_number=1
        )
        self.pipeline_version3 = PipelineVersion.objects.create(
            pipeline=self.pipeline, version_number=3
        )

    def test_create_template(self):
        template = Template.objects.create(
            name="Test Template",
            code="test_code",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )
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

    def test_create_template_version(self):
        template = Template.objects.create(
            name="Test Template",
            code="test_code",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )
        template_version1 = template.create_version(self.pipeline_version1)
        self.assertEqual(template_version1.version_number, 1)
        self.assertEqual(template_version1.template, template)
        self.assertEqual(
            template_version1.source_pipeline_version, self.pipeline_version1
        )

        template_version2 = template.create_version(self.pipeline_version3)
        self.assertEqual(template_version2.version_number, 2)
        self.assertEqual(template_version2.template, template)
        self.assertEqual(
            template_version2.source_pipeline_version, self.pipeline_version3
        )

        self.assertEqual(template.versions.count(), 2)


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
