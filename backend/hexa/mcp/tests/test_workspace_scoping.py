from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.utils import timezone
from oauth2_provider.models import Application

from hexa.datasets.models import Dataset, DatasetVersion, DatasetVersionFile
from hexa.mcp.models import MCPConnection, MCPUser
from hexa.mcp.tests.testutils import all_tool_names
from hexa.mcp.tools.datasets import preview_dataset_file
from hexa.mcp.tools.pipelines import get_pipeline_run, run_pipeline, update_pipeline
from hexa.mcp.tools.templates import (
    create_pipeline_from_template,
    get_pipeline_template,
    list_pipeline_templates,
)
from hexa.mcp.tools.webapps import edit_static_webapp_file, update_static_webapp
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.pipelines.models import (
    Pipeline,
    PipelineRun,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineVersion,
)
from hexa.webapps.models import Webapp
from hexa.workspaces.tests.testutils import create_workspace

from .testutils import MCPTestCase


def _mock_forgejo():
    client = MagicMock()
    client.get_commits.return_value = [{"id": "a" * 40}]
    client.commit_files.return_value = "a" * 40
    client.get_repository_files.return_value = []
    return patch("hexa.git.mixins.get_forgejo_client", return_value=client)


class OpaqueIdScopingTest(MCPTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.UNGRANTED_WORKSPACE = create_workspace(
            cls.USER_ADMIN, name="Ungranted Workspace"
        )

        cls.OTHER_PIPELINE = Pipeline.objects.create(
            workspace=cls.UNGRANTED_WORKSPACE,
            name="Other Pipeline",
            code="other-pipeline",
        )
        cls.OTHER_PIPELINE_VERSION = PipelineVersion.objects.create(
            pipeline=cls.OTHER_PIPELINE,
            user=cls.USER_ADMIN,
            zipfile=cls.ZIP_CONTENT,
            parameters=[],
        )
        cls.OTHER_RUN = PipelineRun.objects.create(
            pipeline=cls.OTHER_PIPELINE,
            pipeline_version=cls.OTHER_PIPELINE_VERSION,
            user=cls.USER_ADMIN,
            run_id="other-run-1",
            execution_date=timezone.now(),
            trigger_mode=PipelineRunTrigger.MANUAL,
            state=PipelineRunState.SUCCESS,
            duration=timedelta(seconds=1),
            config={},
        )

        cls.OTHER_DATASET = Dataset.objects.create_if_has_perm(
            cls.USER_ADMIN,
            workspace=cls.UNGRANTED_WORKSPACE,
            name="Other Dataset",
            description="",
        )
        cls.OTHER_DATASET_VERSION = DatasetVersion.objects.create_if_has_perm(
            cls.USER_ADMIN,
            dataset=cls.OTHER_DATASET,
            name="v1",
            changelog="",
        )
        cls.OTHER_DATASET_FILE = DatasetVersionFile.objects.create_if_has_perm(
            cls.USER_ADMIN,
            dataset_version=cls.OTHER_DATASET_VERSION,
            uri="other-file.csv",
            content_type="text/csv",
        )

        cls.OTHER_WEBAPP = Webapp.objects.create(
            name="Other Webapp",
            slug="other-webapp",
            subdomain="other-webapp",
            workspace=cls.UNGRANTED_WORKSPACE,
            created_by=cls.USER_ADMIN,
        )

        cls.OTHER_TEMPLATE = PipelineTemplate.objects.create(
            name="Other Template",
            code="other-template",
            workspace=cls.UNGRANTED_WORKSPACE,
            source_pipeline=cls.OTHER_PIPELINE,
        )
        cls.OTHER_TEMPLATE_VERSION = PipelineTemplateVersion.objects.create(
            template=cls.OTHER_TEMPLATE,
            version_number=1,
            user=cls.USER_ADMIN,
            source_pipeline_version=cls.OTHER_PIPELINE_VERSION,
        )

        cls.APPLICATION = Application.objects.create(
            name="Claude",
            client_id="scoping-test-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        cls.GRANT = MCPConnection.objects.create(
            user=cls.USER_ADMIN,
            application=cls.APPLICATION,
            tools=all_tool_names(),
        )
        cls.GRANT.workspaces.set([cls.WORKSPACE])

    def setUp(self):
        super().setUp()
        self.mcp_user = MCPUser.from_user(self.USER_ADMIN, self.GRANT)

    def test_the_person_can_reach_both_workspaces(self):
        self.assertEqual(
            "Other Pipeline",
            get_pipeline_run(user=self.USER_ADMIN, run_id=str(self.OTHER_RUN.id))[
                "pipeline"
            ]["name"],
        )

    def test_a_run_in_an_ungranted_workspace_is_invisible(self):
        result = get_pipeline_run(user=self.mcp_user, run_id=str(self.OTHER_RUN.id))

        self.assertEqual({"error": "Pipeline run not found"}, result)

    def test_a_run_in_the_granted_workspace_is_visible(self):
        result = get_pipeline_run(user=self.mcp_user, run_id=str(self.PIPELINE_RUN.id))

        self.assertEqual("Test Pipeline", result["pipeline"]["name"])

    def test_a_pipeline_in_an_ungranted_workspace_cannot_be_run(self):
        result = run_pipeline(
            user=self.mcp_user, pipeline_id=str(self.OTHER_PIPELINE.id)
        )

        self.assertFalse(result["success"])
        self.assertIn("PIPELINE_NOT_FOUND", result["errors"])

    def test_a_pipeline_in_an_ungranted_workspace_cannot_be_updated(self):
        result = update_pipeline(
            user=self.mcp_user,
            pipeline_id=str(self.OTHER_PIPELINE.id),
            name="Renamed",
        )

        self.assertFalse(result["success"])
        self.OTHER_PIPELINE.refresh_from_db()
        self.assertEqual("Other Pipeline", self.OTHER_PIPELINE.name)

    def test_a_dataset_file_in_an_ungranted_workspace_is_invisible(self):
        result = preview_dataset_file(
            user=self.mcp_user, file_id=str(self.OTHER_DATASET_FILE.id)
        )

        self.assertEqual({"error": "Dataset file not found"}, result)

    def test_a_dataset_file_in_the_granted_workspace_is_visible(self):
        result = preview_dataset_file(
            user=self.mcp_user, file_id=str(self.DATASET_FILE.id)
        )

        self.assertEqual("test-file.csv", result["filename"])

    def test_a_webapp_in_an_ungranted_workspace_cannot_be_updated(self):
        with _mock_forgejo():
            result = update_static_webapp(
                user=self.mcp_user,
                webapp_id=str(self.OTHER_WEBAPP.id),
                name="Renamed",
            )

        self.assertFalse(result["success"])
        self.OTHER_WEBAPP.refresh_from_db()
        self.assertEqual("Other Webapp", self.OTHER_WEBAPP.name)

    def test_a_webapp_file_in_an_ungranted_workspace_cannot_be_edited(self):
        with _mock_forgejo():
            result = edit_static_webapp_file(
                user=self.mcp_user,
                webapp_id=str(self.OTHER_WEBAPP.id),
                path="index.html",
                old_string="a",
                new_string="b",
            )

        self.assertFalse(result["success"])

    def test_a_template_version_in_an_ungranted_workspace_cannot_be_instantiated(self):
        result = create_pipeline_from_template(
            user=self.mcp_user,
            workspace_slug=self.UNGRANTED_WORKSPACE.slug,
            template_version_id=str(self.OTHER_TEMPLATE_VERSION.id),
        )

        self.assertFalse(result["success"])
        self.assertFalse(
            Pipeline.objects.filter(workspace=self.UNGRANTED_WORKSPACE)
            .exclude(pk=self.OTHER_PIPELINE.pk)
            .exists()
        )

    def test_templates_from_ungranted_workspaces_are_still_listed(self):
        result = list_pipeline_templates(user=self.mcp_user)
        codes = {t["code"] for t in result["pipelineTemplates"]["items"]}

        self.assertIn("other-template", codes)

    def test_a_template_from_an_ungranted_workspace_is_still_readable(self):
        result = get_pipeline_template(
            user=self.mcp_user, template_code="other-template"
        )

        self.assertEqual("Other Template", result["name"])
