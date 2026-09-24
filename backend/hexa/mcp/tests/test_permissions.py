import json

from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.test import SimpleTestCase, TestCase
from oauth2_provider.models import Application

from hexa.mcp.models import MCPConnection, MCPUser, ToolCall
from hexa.mcp.protocol import (
    call_tool,
    get_tools_catalogue,
    handle_jsonrpc,
    tool,
)
from hexa.mcp.tests.testutils import advertised_tool_names, all_tool_names
from hexa.user_management.models import User


class ToolListFilteringTest(SimpleTestCase):
    def test_no_connection_returns_the_whole_catalogue(self):
        names = advertised_tool_names()

        self.assertIn("write_file", names)
        self.assertIn("list_datasets", names)
        self.assertIn("get_help_or_doc", names)

    def test_only_the_granted_tools_are_advertised(self):
        connection = MCPConnection(tools=["list_files", "read_file"])

        names = advertised_tool_names(connection)

        self.assertIn("list_files", names)
        self.assertIn("read_file", names)
        self.assertNotIn("write_file", names)
        self.assertNotIn("list_datasets", names)

    def test_a_full_grant_advertises_the_whole_catalogue(self):
        connection = MCPConnection(tools=all_tool_names())

        self.assertEqual(advertised_tool_names(), advertised_tool_names(connection))

    def test_help_needs_no_grant(self):
        self.assertIn("get_help_or_doc", advertised_tool_names(MCPConnection(tools=[])))


class ToolGroupingTest(SimpleTestCase):
    def catalogue(self):
        return {entry["name"]: entry for entry in get_tools_catalogue()}

    def test_a_tool_is_grouped_by_the_module_it_lives_in(self):
        self.assertEqual("DATABASES", self.catalogue()["get_db_schema"]["resource"])
        self.assertEqual("FILES", self.catalogue()["write_file"]["resource"])

    def test_the_help_tool_is_ungated(self):
        self.assertIsNone(self.catalogue()["get_help_or_doc"]["resource"])

    def test_a_tool_in_an_unmapped_module_is_refused(self):
        def a_tool_from_nowhere(user):
            pass

        a_tool_from_nowhere.__module__ = "hexa.mcp.tools.something_new"

        with self.assertRaises(ImproperlyConfigured):
            tool(a_tool_from_nowhere)


class ToolCallEnforcementTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("mcp@openhexa.org", "password")
        cls.APPLICATION = Application.objects.create(
            name="Claude",
            client_id="enforcement-test-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )

    def connection(self, tools):
        return MCPConnection.objects.create(
            user=self.USER, application=self.APPLICATION, tools=tools
        )

    def test_an_ungranted_tool_is_refused(self):
        connection = self.connection(["list_files"])

        with self.assertRaises(PermissionDenied):
            call_tool("list_datasets", {"workspace_slug": "any"}, self.USER, connection)

    def test_the_write_tool_of_a_granted_resource_is_still_refused(self):
        connection = self.connection(["list_files", "read_file"])

        with self.assertRaises(PermissionDenied):
            call_tool(
                "write_file",
                {"workspace_slug": "any", "file_path": "a.txt", "content": "hi"},
                self.USER,
                connection,
            )

    def test_a_refusal_is_recorded(self):
        connection = self.connection([])

        with self.assertRaises(PermissionDenied):
            call_tool("list_files", {"workspace_slug": "any"}, self.USER, connection)

        call = ToolCall.objects.get(tool_name="list_files")
        self.assertFalse(call.success)
        self.assertIn("not authorized", call.error)

    def test_a_cached_tool_still_gets_refused_over_jsonrpc(self):
        connection = self.connection(["list_files"])
        mcp_user = MCPUser.from_user(self.USER, connection)

        response = handle_jsonrpc(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "list_datasets",
                        "arguments": {"workspace_slug": "any"},
                    },
                }
            ).encode(),
            mcp_user,
        )

        self.assertTrue(response["result"]["isError"])
        text = response["result"]["content"][0]["text"]
        self.assertIn("not authorized to call list_datasets", text)
        self.assertNotIn("internal error", text)
        self.assertIn("Claude", text)
        self.assertIn("/user/account#mcp-connections", text)

    def test_tools_list_over_jsonrpc_is_filtered_by_the_grant(self):
        connection = self.connection(["list_files", "read_file"])
        mcp_user = MCPUser.from_user(self.USER, connection)

        response = handle_jsonrpc(
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).encode(),
            mcp_user,
        )

        names = {tool["name"] for tool in response["result"]["tools"]}
        self.assertEqual({"list_files", "read_file", "get_help_or_doc"}, names)
