import json
from unittest.mock import patch

from django.core.exceptions import PermissionDenied
from django.db import models
from django.test import RequestFactory, SimpleTestCase
from oauth2_provider.models import Application

from hexa.data_studio.templating import PARAMETER_TYPES
from hexa.mcp.models import MCPConnection, MCPResource, MCPUser
from hexa.mcp.protocol import (
    _TOOLS,
    RegisteredTool,
    _get_tool_schema,
    call_tool,
    get_tools_list,
)
from hexa.mcp.tools.pipelines import create_pipeline
from hexa.mcp.tools.saved_queries import create_saved_query
from hexa.mcp.tools.webapps import create_static_webapp, get_static_webapp_file
from hexa.mcp.views import mcp_endpoint
from hexa.pipelines.models import PipelineFunctionalType
from hexa.webapps.models import Webapp

from .testutils import MCPTestCase, all_tool_names


class _Color(models.TextChoices):
    RED = "red", "Red"
    GREEN = "green", "Green"


class _Priority(models.IntegerChoices):
    LOW = 1, "Low"
    HIGH = 2, "High"


def _sample_tool(
    user,
    name: str,
    start_line: int | None = None,
    page: int = 1,
    ratio: float = 1.0,
    color: _Color = _Color.RED,
    priority: _Priority | None = None,
):
    pass


def _list_tool(
    user,
    tags: list[str],
    counts: list[int],
    ratios: list[float],
    flags: list[bool],
    colors: list[_Color],
    optional_tags: list[str] | None = None,
    mapping: dict[str, int] = None,
):
    pass


class ToolSchemaTest(SimpleTestCase):
    def test_optional_int_is_advertised_as_integer(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertEqual(schema["properties"]["start_line"]["type"], "integer")
        self.assertEqual(schema["properties"]["page"]["type"], "integer")
        self.assertEqual(schema["properties"]["ratio"]["type"], "number")
        self.assertEqual(schema["properties"]["name"]["type"], "string")

    def test_user_arg_is_excluded(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertNotIn("user", schema["properties"])

    def test_required_are_args_without_defaults(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertEqual(schema["required"], ["name"])

    def test_optional_int_arg_is_not_required(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertNotIn("start_line", schema["required"])

    def test_webapp_file_line_range_is_optional_integer(self):
        schema = _get_tool_schema(get_static_webapp_file)
        for arg in ("start_line", "end_line"):
            self.assertEqual(schema["properties"][arg]["type"], "integer")
            self.assertNotIn(arg, schema["required"])
        self.assertEqual(schema["required"], ["workspace_slug", "webapp_slug", "path"])

    def test_text_choices_is_string_enum(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertEqual(
            schema["properties"]["color"],
            {"type": "string", "enum": ["red", "green"]},
        )

    def test_integer_choices_is_integer_enum(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertEqual(
            schema["properties"]["priority"],
            {"type": "integer", "enum": [1, 2]},
        )

    def test_optional_enum_is_not_required(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertNotIn("priority", schema["required"])

    def test_list_generics_become_typed_arrays(self):
        properties = _get_tool_schema(_list_tool)["properties"]
        self.assertEqual(
            properties["tags"], {"type": "array", "items": {"type": "string"}}
        )
        self.assertEqual(
            properties["counts"], {"type": "array", "items": {"type": "integer"}}
        )
        self.assertEqual(
            properties["ratios"], {"type": "array", "items": {"type": "number"}}
        )
        self.assertEqual(
            properties["flags"], {"type": "array", "items": {"type": "boolean"}}
        )

    def test_optional_list_is_unwrapped_to_array(self):
        properties = _get_tool_schema(_list_tool)["properties"]
        self.assertEqual(
            properties["optional_tags"], {"type": "array", "items": {"type": "string"}}
        )

    def test_list_of_enum_is_array_of_enum(self):
        properties = _get_tool_schema(_list_tool)["properties"]
        self.assertEqual(
            properties["colors"],
            {"type": "array", "items": {"type": "string", "enum": ["red", "green"]}},
        )

    def test_dict_is_an_object(self):
        properties = _get_tool_schema(_list_tool)["properties"]
        self.assertEqual(properties["mapping"], {"type": "object"})

    def test_list_of_typed_dict_is_an_array_of_described_objects(self):
        schema = _get_tool_schema(create_saved_query)
        self.assertEqual(
            schema["properties"]["parameters"],
            {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string", "enum": list(PARAMETER_TYPES)},
                        "multiple": {"type": "boolean"},
                        "required": {"type": "boolean"},
                        "default": {},
                        "help": {"type": "string"},
                    },
                    "required": ["name", "type"],
                },
            },
        )
        self.assertNotIn("parameters", schema["required"])

    def test_create_pipeline_functional_type_exposes_graphql_values(self):
        schema = _get_tool_schema(create_pipeline)
        prop = schema["properties"]["functional_type"]
        self.assertEqual(prop["type"], "string")
        self.assertEqual(set(prop["enum"]), {c.value for c in PipelineFunctionalType})
        self.assertIn("extraction", prop["enum"])
        self.assertNotIn("functional_type", schema["required"])


class ToolsListTest(SimpleTestCase):
    def test_create_pipeline_advertises_functional_type_enum(self):
        tools = {t["name"]: t for t in get_tools_list()}
        self.assertIn("create_pipeline", tools)
        prop = tools["create_pipeline"]["inputSchema"]["properties"]["functional_type"]
        self.assertEqual(prop["type"], "string")
        self.assertEqual(set(prop["enum"]), {c.value for c in PipelineFunctionalType})

    def test_create_static_webapp_advertises_allowed_operations_enum(self):
        schema = _get_tool_schema(create_static_webapp)
        prop = schema["properties"]["allowed_operations"]
        self.assertEqual(prop["type"], "array")
        self.assertEqual(prop["items"]["type"], "string")
        self.assertEqual(
            set(prop["items"]["enum"]), {c.value for c in Webapp.OperationScope}
        )
        self.assertIn("PIPELINES_READ", prop["items"]["enum"])
        self.assertNotIn("allowed_operations", schema["required"])


class ToolCallAnalyticsTest(MCPTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.APPLICATION = Application.objects.create(
            name="Claude",
            client_id="protocol-analytics-test-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        cls.MCP_CONNECTION = MCPConnection.objects.create(
            user=cls.USER_VIEWER,
            application=cls.APPLICATION,
            tools=all_tool_names(),
        )
        cls.MCP_CONNECTION.workspaces.set([cls.WORKSPACE])

    def setUp(self):
        super().setUp()
        self.mcp_user = MCPUser.from_user(self.USER_VIEWER, self.MCP_CONNECTION)

    @patch("hexa.mcp.protocol.track")
    def test_successful_tool_call_tracks_event(self, mock_track):
        call_tool(
            "list_datasets",
            {"workspace_slug": self.WORKSPACE.slug},
            self.mcp_user,
            self.MCP_CONNECTION,
        )

        mock_track.assert_called_once_with(
            None,
            "mcp.tool_called",
            {
                "tool_name": "list_datasets",
                "resource": MCPResource.DATASETS,
                "write": False,
                "status": "success",
                "workspace": self.WORKSPACE.slug,
                "client": "Claude",
            },
            user=self.USER_VIEWER,
        )
        self.assertIs(mock_track.call_args.kwargs["user"], self.USER_VIEWER)

    @patch("hexa.mcp.protocol.track")
    def test_optional_properties_omitted_without_workspace_or_connection(
        self, mock_track
    ):
        call_tool("get_help_or_doc", {"topic": "pipelines"}, self.USER_VIEWER, None)

        mock_track.assert_called_once_with(
            None,
            "mcp.tool_called",
            {
                "tool_name": "get_help_or_doc",
                "resource": None,
                "write": False,
                "status": "success",
            },
            user=self.USER_VIEWER,
        )

    @patch("hexa.mcp.protocol.track")
    def test_refused_disabled_tool_tracks_refused_status(self, mock_track):
        self.MCP_CONNECTION.tools = ["list_files"]
        self.MCP_CONNECTION.save()

        with self.assertRaises(PermissionDenied):
            call_tool(
                "create_dataset",
                {
                    "workspace_slug": self.WORKSPACE.slug,
                    "name": "Secret dataset",
                    "files_json": "[]",
                },
                self.mcp_user,
                self.MCP_CONNECTION,
            )

        mock_track.assert_called_once_with(
            None,
            "mcp.tool_called",
            {
                "tool_name": "create_dataset",
                "resource": MCPResource.DATASETS,
                "write": True,
                "status": "refused",
                "workspace": self.WORKSPACE.slug,
                "client": "Claude",
            },
            user=self.USER_VIEWER,
        )

    @patch("hexa.mcp.protocol.track")
    def test_refused_ungranted_workspace_tracks_refused_status(self, mock_track):
        with self.assertRaises(PermissionDenied):
            call_tool(
                "list_datasets",
                {"workspace_slug": "ungranted-workspace"},
                self.mcp_user,
                self.MCP_CONNECTION,
            )

        mock_track.assert_called_once_with(
            None,
            "mcp.tool_called",
            {
                "tool_name": "list_datasets",
                "resource": MCPResource.DATASETS,
                "write": False,
                "status": "refused",
                "workspace": "ungranted-workspace",
                "client": "Claude",
            },
            user=self.USER_VIEWER,
        )

    @patch("hexa.mcp.protocol.track")
    def test_failing_tool_call_tracks_error_status(self, mock_track):
        def boom(user, workspace_slug: str):
            raise RuntimeError("boom")

        self.MCP_CONNECTION.tools = [*self.MCP_CONNECTION.tools, "failing_tool"]
        self.MCP_CONNECTION.save()

        with patch.dict(
            _TOOLS,
            {
                "failing_tool": RegisteredTool(
                    func=boom, resource=MCPResource.DATASETS, write=True
                )
            },
        ):
            with self.assertRaises(RuntimeError):
                call_tool(
                    "failing_tool",
                    {"workspace_slug": self.WORKSPACE.slug},
                    self.mcp_user,
                    self.MCP_CONNECTION,
                )

        mock_track.assert_called_once_with(
            None,
            "mcp.tool_called",
            {
                "tool_name": "failing_tool",
                "resource": MCPResource.DATASETS,
                "write": True,
                "status": "error",
                "workspace": self.WORKSPACE.slug,
                "client": "Claude",
            },
            user=self.USER_VIEWER,
        )

    @patch("hexa.mcp.protocol.track")
    def test_mcp_endpoint_forwards_request_to_track(self, mock_track):
        request = RequestFactory().post(
            "/mcp/",
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "list_datasets",
                        "arguments": {"workspace_slug": self.WORKSPACE.slug},
                    },
                }
            ),
            content_type="application/json",
        )
        request.user = self.mcp_user

        response = mcp_endpoint(request)

        self.assertEqual(response.status_code, 200)
        mock_track.assert_called_once_with(
            request,
            "mcp.tool_called",
            {
                "tool_name": "list_datasets",
                "resource": MCPResource.DATASETS,
                "write": False,
                "status": "success",
                "workspace": self.WORKSPACE.slug,
                "client": "Claude",
            },
            user=self.USER_VIEWER,
        )
        self.assertIs(mock_track.call_args.args[0], request)

    @patch("hexa.mcp.protocol.track")
    def test_raw_tool_arguments_are_not_sent_to_mixpanel(self, mock_track):
        secret_sql = "SELECT email, ssn FROM sensitive_patients"
        call_tool(
            "list_workspaces",
            {"query": secret_sql},
            self.mcp_user,
            self.MCP_CONNECTION,
        )

        properties = mock_track.call_args.args[2]
        self.assertNotIn("arguments", properties)
        self.assertNotIn("query", properties)
        self.assertNotIn(secret_sql, json.dumps(properties))
