import json
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.core.exceptions import PermissionDenied
from django.utils import timezone
from oauth2_provider.models import Application
from pydantic_ai.models.test import TestModel

from hexa.assistant.agents import _AGENT_REGISTRY
from hexa.assistant.models import Conversation
from hexa.assistant.tests.agents._helpers import FakeModelBuilder
from hexa.data_studio.models import SavedQuery, SavedQueryVisibility
from hexa.datasets.models import (
    Dataset,
    DatasetLink,
    DatasetVersion,
    DatasetVersionFile,
    DatasetVisibility,
)
from hexa.mcp.models import MCPConnection, MCPUser
from hexa.mcp.protocol import _TOOLS, ai_disabled_message, call_tool
from hexa.mcp.tests.testutils import all_tool_names
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

# Only ever written into the blocked workspace's content, never into an identifier
# passed to a tool, so finding it in a tool's output means that content leaked.
MARKER = "classified"


def _mock_forgejo():
    client = MagicMock()
    client.get_commits.return_value = [{"id": "a" * 40}]
    client.commit_files.return_value = "a" * 40
    client.get_repository_files.return_value = []
    client.get_file.return_value = b"<html>classified</html>"
    return patch("hexa.git.mixins.get_forgejo_client", return_value=client)


class AiDisabledWorkspaceTest(MCPTestCase):
    """Every tool, called from an allowed workspace, keeps away from the content of a
    workspace whose admins blocked AI: through MCP, and as the in-app assistant's
    agents hold them.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.BLOCKED = create_workspace(
                cls.USER_ADMIN,
                name="Blocked Workspace",
                organization=cls.WORKSPACE.organization,
            )
        cls.BLOCKED.description = "Classified notes"

        cls.SECRET_PIPELINE = Pipeline.objects.create(
            workspace=cls.BLOCKED, name="Classified Pipeline", code="pipe-a"
        )
        secret_version = PipelineVersion.objects.create(
            pipeline=cls.SECRET_PIPELINE,
            user=cls.USER_ADMIN,
            zipfile=cls.ZIP_CONTENT,
            parameters=[],
        )
        cls.SECRET_RUN = PipelineRun.objects.create(
            pipeline=cls.SECRET_PIPELINE,
            pipeline_version=secret_version,
            user=cls.USER_ADMIN,
            run_id="run-a",
            execution_date=timezone.now(),
            trigger_mode=PipelineRunTrigger.MANUAL,
            state=PipelineRunState.SUCCESS,
            duration=timedelta(seconds=1),
            config={"note": "classified"},
        )

        cls.SECRET_DATASET = Dataset.objects.create_if_has_perm(
            cls.USER_ADMIN,
            workspace=cls.BLOCKED,
            name="Classified Dataset",
            description="",
        )
        Dataset.objects.filter(pk=cls.SECRET_DATASET.pk).update(slug="ds-a")
        cls.SECRET_DATASET.refresh_from_db()
        cls.SECRET_DATASET.link(cls.USER_ADMIN, cls.WORKSPACE)
        secret_dataset_version = DatasetVersion.objects.create_if_has_perm(
            cls.USER_ADMIN, dataset=cls.SECRET_DATASET, name="v1", changelog=""
        )
        cls.SECRET_FILE = DatasetVersionFile.objects.create_if_has_perm(
            cls.USER_ADMIN,
            dataset_version=secret_dataset_version,
            uri="classified.csv",
            content_type="text/csv",
        )

        # Never linked anywhere: reachable only because it is shared organization-wide.
        cls.ORG_DATASET = Dataset.objects.create_if_has_perm(
            cls.USER_ADMIN,
            workspace=cls.BLOCKED,
            name="Classified Org Dataset",
            description="",
        )
        Dataset.objects.filter(pk=cls.ORG_DATASET.pk).update(
            slug="ds-org", visibility=DatasetVisibility.ORGANIZATION
        )
        cls.ORG_DATASET.refresh_from_db()
        org_dataset_version = DatasetVersion.objects.create_if_has_perm(
            cls.USER_ADMIN, dataset=cls.ORG_DATASET, name="v1", changelog=""
        )
        cls.ORG_FILE = DatasetVersionFile.objects.create_if_has_perm(
            cls.USER_ADMIN,
            dataset_version=org_dataset_version,
            uri="classified-org.csv",
            content_type="text/csv",
        )

        cls.SECRET_TEMPLATE = PipelineTemplate.objects.create(
            name="Classified Template",
            code="tpl-a",
            workspace=cls.BLOCKED,
            source_pipeline=cls.SECRET_PIPELINE,
        )
        cls.SECRET_TEMPLATE_VERSION = PipelineTemplateVersion.objects.create(
            template=cls.SECRET_TEMPLATE,
            version_number=1,
            user=cls.USER_ADMIN,
            source_pipeline_version=secret_version,
        )

        cls.SECRET_WEBAPP = Webapp.objects.create(
            name="Classified Webapp",
            slug="app-a",
            subdomain="app-a",
            workspace=cls.BLOCKED,
            created_by=cls.USER_ADMIN,
        )

        cls.SECRET_QUERY = SavedQuery.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.BLOCKED,
            name="Classified query",
            content="SELECT 'classified'",
            visibility=SavedQueryVisibility.WORKSPACE,
        )
        SavedQuery.objects.filter(pk=cls.SECRET_QUERY.pk).update(slug="query-a")
        cls.SECRET_QUERY.refresh_from_db()

        cls.CONNECTION = MCPConnection.objects.create(
            user=cls.USER_ADMIN,
            application=Application.objects.create(
                name="Claude",
                client_id="ai-disabled-test-client",
                client_type=Application.CLIENT_PUBLIC,
                authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            ),
            tools=all_tool_names(),
        )
        cls.CONNECTION.workspaces.set([cls.WORKSPACE, cls.BLOCKED])

        cls.BLOCKED.ai_enabled = False
        cls.BLOCKED.save()

    def setUp(self):
        super().setUp()
        self.mcp_user = MCPUser.from_user(self.USER_ADMIN, self.CONNECTION)

    def scenarios(self) -> dict[str, list[dict]]:
        """For each tool, the calls from the allowed workspace aimed at the blocked one."""
        allowed = self.WORKSPACE.slug
        scenarios = {
            "get_help_or_doc": {},
            "list_workspaces": {},
            "get_workspace": {"slug": allowed},
            "update_workspace": {"slug": allowed, "description": "Updated"},
            "list_files": {"workspace_slug": allowed},
            "glob_files": {"workspace_slug": allowed, "pattern": "**"},
            "grep_files": {"workspace_slug": allowed, "pattern": ".", "glob": "**"},
            "read_file": {"workspace_slug": allowed, "file_path": "a.txt"},
            "write_file": {
                "workspace_slug": allowed,
                "file_path": "a.txt",
                "content": "a",
            },
            "list_datasets": {"workspace_slug": allowed},
            "get_dataset": [
                {"workspace_slug": allowed, "dataset_slug": "ds-a"},
                {"workspace_slug": allowed, "dataset_slug": "ds-org"},
            ],
            "preview_dataset_file": [
                {"file_id": str(self.SECRET_FILE.id)},
                {"file_id": str(self.ORG_FILE.id)},
            ],
            "create_dataset": {
                "workspace_slug": allowed,
                "name": "New",
                "files_json": json.dumps(
                    [{"uri": "a.csv", "contentType": "text/csv", "content": "a,b"}]
                ),
            },
            "create_dataset_version": {
                "dataset_id": str(self.SECRET_DATASET.id),
                "name": "v2",
            },
            "list_pipelines": {"workspace_slug": allowed},
            "get_pipeline": {"workspace_slug": allowed, "pipeline_code": "pipe-a"},
            "get_pipeline_run": {"run_id": str(self.SECRET_RUN.id)},
            "run_pipeline": {"pipeline_id": str(self.SECRET_PIPELINE.id)},
            "update_pipeline": {
                "pipeline_id": str(self.SECRET_PIPELINE.id),
                "name": "Renamed",
            },
            "create_pipeline": {
                "workspace_slug": allowed,
                "name": "New",
                "files_json": "[]",
            },
            "create_pipeline_version": {
                "workspace_slug": allowed,
                "pipeline_code": "pipe-a",
                "files_json": "[]",
            },
            "list_static_webapps": {"workspace_slug": allowed},
            "get_static_webapp": {"workspace_slug": allowed, "webapp_slug": "app-a"},
            "get_static_webapp_file": {
                "workspace_slug": allowed,
                "webapp_slug": "app-a",
                "path": "index.html",
            },
            "create_static_webapp": {
                "workspace_slug": allowed,
                "name": "New",
                "files_json": "[]",
            },
            "update_static_webapp": {
                "webapp_id": str(self.SECRET_WEBAPP.id),
                "name": "Renamed",
            },
            "edit_static_webapp_file": {
                "webapp_id": str(self.SECRET_WEBAPP.id),
                "path": "index.html",
                "old_string": "classified",
                "new_string": "public",
            },
            "get_db_schema": {"workspace_slug": allowed},
            "get_db_table_schema": {"workspace_slug": allowed, "table_name": "a"},
            "list_connections": {"workspace_slug": allowed},
            "list_saved_queries": {"workspace_slug": allowed},
            "get_saved_query": {"saved_query_slug": "query-a"},
            "create_saved_query": {
                "workspace_slug": allowed,
                "name": "New",
                "content": "SELECT 1",
            },
            "update_saved_query": {
                "saved_query_id": str(self.SECRET_QUERY.id),
                "name": "Renamed",
            },
            "list_pipeline_templates": {},
            "get_pipeline_template": {"template_code": "tpl-a"},
            "create_pipeline_from_template": {
                "workspace_slug": allowed,
                "template_version_id": str(self.SECRET_TEMPLATE_VERSION.id),
            },
        }
        return {
            name: calls if isinstance(calls, list) else [calls]
            for name, calls in scenarios.items()
        }

    def calls(self):
        for name, calls in self.scenarios().items():
            for arguments in calls:
                yield name, arguments

    def snapshot(self) -> dict:
        """What a write to the blocked workspace's content would change."""
        return {
            "pipeline": Pipeline.objects.get(pk=self.SECRET_PIPELINE.pk).name,
            "runs": PipelineRun.objects.filter(pipeline=self.SECRET_PIPELINE).count(),
            "dataset_versions": DatasetVersion.objects.filter(
                dataset=self.SECRET_DATASET
            ).count(),
            "webapp": Webapp.objects.get(pk=self.SECRET_WEBAPP.pk).name,
            "query": SavedQuery.objects.get(pk=self.SECRET_QUERY.pk).name,
            "from_template": Pipeline.objects.filter(
                source_template=self.SECRET_TEMPLATE
            ).count(),
        }

    def assistant_tools(self) -> dict[str, list]:
        """For each tool, the functions the assistant's agents call it through, as
        bound to a conversation in the allowed workspace.
        """
        tools: dict[str, list] = {}
        for instruction_set, agent_class in _AGENT_REGISTRY.items():
            conversation = Conversation.objects.create(
                user=self.USER_ADMIN,
                workspace=self.WORKSPACE,
                instruction_set=instruction_set,
            )
            agent = agent_class(conversation, FakeModelBuilder(TestModel()))
            for func in agent._tools_with_context:
                tools.setdefault(func.__name__, []).append(func)
        return tools

    def call(self, user, name: str, arguments: dict) -> tuple[str, Exception | None]:
        """The tool's output as text, or the exception it raised."""
        try:
            with _mock_forgejo():
                if isinstance(user, MCPUser):
                    result = call_tool(name, arguments, user, user.connection)
                else:
                    result = _TOOLS[name].func(user=user, **arguments)
        except Exception as error:
            return "", error
        return json.dumps(result, default=str), None

    def call_as_assistant(self, func, arguments: dict) -> tuple[str, Exception | None]:
        """Like `call`, with the model asking for the blocked workspace in place of
        any workspace argument the agent binds.
        """
        aimed = {
            key: self.BLOCKED.slug if key in ("workspace_slug", "slug") else value
            for key, value in arguments.items()
        }
        try:
            with _mock_forgejo():
                result = func(**aimed)
        except Exception as error:
            return "", error
        return json.dumps(result, default=str), None

    def test_every_tool_has_a_scenario(self):
        missing = set(_TOOLS) - set(self.scenarios())
        self.assertFalse(
            missing,
            f"Add a scenario for {sorted(missing)} to show it cannot reach the "
            f"content of a workspace whose admins blocked AI.",
        )

    def test_no_tool_reaches_the_blocked_workspace_through_mcp(self):
        before = self.snapshot()
        for name, arguments in self.calls():
            with self.subTest(tool=name, **arguments):
                output, error = self.call(self.mcp_user, name, arguments)

                # A tool that crashes returns nothing, which would pass for the
                # wrong reason: the scenario must reach the tool's own checks.
                self.assertIsNone(error)
                self.assertNotIn(MARKER, output.lower())
                self.assertEqual(before, self.snapshot())

    def test_no_assistant_tool_reaches_the_blocked_workspace(self):
        tools = self.assistant_tools()
        before = self.snapshot()
        for name, arguments in self.calls():
            for func in tools.get(name, []):
                with self.subTest(tool=name, **arguments):
                    output, error = self.call_as_assistant(func, arguments)

                    self.assertIsNone(error)
                    self.assertNotIn(MARKER, output.lower())
                    self.assertEqual(before, self.snapshot())

    def test_the_scenarios_reach_the_content_when_ai_is_allowed(self):
        """Guards the test above: without the block, the same calls do leak."""
        self.BLOCKED.ai_enabled = True
        self.BLOCKED.save()

        for name, arguments in self.calls():
            if name not in (
                "list_datasets",
                "get_dataset",
                "preview_dataset_file",
                "get_pipeline_run",
                "get_saved_query",
                "list_pipeline_templates",
                "get_pipeline_template",
            ):
                continue
            with self.subTest(tool=name, **arguments):
                output, _ = self.call(self.USER_ADMIN, name, arguments)

                self.assertIn(MARKER, output.lower())

    def test_mcp_refuses_every_workspace_tool_on_the_blocked_workspace(self):
        for name, arguments in self.calls():
            slug_argument = next(
                (key for key in ("workspace_slug", "slug") if key in arguments), None
            )
            if slug_argument is None:
                continue
            with self.subTest(tool=name):
                with self.assertRaisesMessage(
                    PermissionDenied, ai_disabled_message(self.BLOCKED.slug)
                ):
                    call_tool(
                        name,
                        {**arguments, slug_argument: self.BLOCKED.slug},
                        self.mcp_user,
                        self.CONNECTION,
                    )

    def test_the_blocked_workspace_is_not_granted(self):
        self.assertEqual([self.WORKSPACE.id], self.mcp_user.workspace_ids)

    def test_allowing_ai_again_restores_the_grant(self):
        self.BLOCKED.update_if_has_perm(principal=self.USER_ADMIN, ai_enabled=True)

        self.assertIn(
            self.BLOCKED.slug,
            MCPUser.from_user(self.USER_ADMIN, self.CONNECTION).granted_workspaces,
        )

    def test_an_organization_grant_leaves_the_blocked_workspace_out(self):
        self.CONNECTION.workspaces.clear()
        self.CONNECTION.organizations.set([self.WORKSPACE.organization])

        mcp_user = MCPUser.from_user(self.USER_ADMIN, self.CONNECTION)

        self.assertIn(self.WORKSPACE.slug, mcp_user.granted_workspaces)
        self.assertNotIn(self.BLOCKED.slug, mcp_user.granted_workspaces)

    def test_listings_leave_the_blocked_workspace_out_before_paginating(self):
        datasets, _ = self.call(
            self.mcp_user,
            "list_datasets",
            {"workspace_slug": self.WORKSPACE.slug, "per_page": 1},
        )
        templates, _ = self.call(self.mcp_user, "list_pipeline_templates", {})

        visible_links = DatasetLink.objects.filter_for_workspaces(
            workspaces=[self.WORKSPACE]
        ).exclude(dataset__workspace=self.BLOCKED)
        page = json.loads(datasets)["datasets"]
        self.assertEqual(visible_links.count(), page["totalItems"])
        self.assertEqual(1, len(page["items"]))
        self.assertEqual(
            PipelineTemplate.objects.exclude(workspace=self.BLOCKED).count(),
            json.loads(templates)["pipelineTemplates"]["totalItems"],
        )

    def test_searching_for_the_blocked_workspace_says_ai_is_disabled(self):
        output, _ = self.call(self.mcp_user, "list_workspaces", {"query": "Blocked"})

        self.assertIn(
            ai_disabled_message(self.BLOCKED.slug), json.loads(output)["message"]
        )
