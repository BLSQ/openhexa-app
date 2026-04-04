from hexa.mcp.tools.templates import (
    create_pipeline_from_template,
    get_pipeline_template,
    list_pipeline_templates,
)
from hexa.pipelines.models import Pipeline

from .testutils import MCPTestCase


class ListPipelineTemplatesTest(MCPTestCase):
    def test_list_pipeline_templates(self):
        result = list_pipeline_templates(user=self.USER_ADMIN)
        templates = result["pipelineTemplates"]
        self.assertEqual(templates["totalItems"], 1)
        self.assertEqual(templates["items"][0]["code"], "test-template")

    def test_list_pipeline_templates_search(self):
        result = list_pipeline_templates(
            user=self.USER_ADMIN, search="nonexistent-template-xyz"
        )
        self.assertEqual(result["pipelineTemplates"]["totalItems"], 0)

    def test_list_pipeline_templates_search_matching(self):
        result = list_pipeline_templates(user=self.USER_ADMIN, search="Test Template")
        self.assertEqual(result["pipelineTemplates"]["totalItems"], 1)
        self.assertEqual(
            result["pipelineTemplates"]["items"][0]["code"], "test-template"
        )


class GetPipelineTemplateTest(MCPTestCase):
    def test_get_pipeline_template(self):
        result = get_pipeline_template(
            user=self.USER_ADMIN, template_code="test-template"
        )
        self.assertEqual(result["name"], "Test Template")
        self.assertEqual(result["code"], "test-template")
        self.assertIn("currentVersion", result)
        self.assertEqual(result["currentVersion"]["versionNumber"], 1)

    def test_get_pipeline_template_not_found(self):
        result = get_pipeline_template(
            user=self.USER_ADMIN, template_code="nonexistent"
        )
        self.assertEqual(result, {"error": "Template not found"})


class CreatePipelineFromTemplateTest(MCPTestCase):
    def test_create_from_template(self):
        result = create_pipeline_from_template(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            template_version_id=str(self.TEMPLATE_VERSION.id),
        )
        self.assertTrue(result["success"])
        self.assertIn("pipeline", result)
        self.assertTrue(Pipeline.objects.filter(id=result["pipeline"]["id"]).exists())

    def test_create_from_template_invalid_version(self):
        result = create_pipeline_from_template(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            template_version_id="00000000-0000-0000-0000-000000000000",
        )
        self.assertFalse(result["success"])
        self.assertIn("PIPELINE_TEMPLATE_VERSION_NOT_FOUND", result["errors"])

    def test_create_from_template_no_access(self):
        result = create_pipeline_from_template(
            user=self.USER_OUTSIDER,
            workspace_slug=self.WORKSPACE.slug,
            template_version_id=str(self.TEMPLATE_VERSION.id),
        )
        self.assertFalse(result["success"])
        self.assertIn("WORKSPACE_NOT_FOUND", result["errors"])
