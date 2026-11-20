import inspect
import json

from django.core.exceptions import PermissionDenied
from django.test import SimpleTestCase
from oauth2_provider.models import Application

from hexa.mcp.models import MCPConnection, MCPResource, MCPUser, ToolCall
from hexa.mcp.protocol import _TOOLS, call_tool, handle_jsonrpc
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace

from .testutils import MCPTestCase, all_tool_names


class WorkspaceRefusalFixtures(MCPTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.UNGRANTED_WORKSPACE = create_workspace(
            cls.USER_ADMIN, name="More workspace 1"
        )
        WorkspaceMembership.objects.create(
            workspace=cls.UNGRANTED_WORKSPACE,
            user=cls.USER_VIEWER,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.APPLICATION = Application.objects.create(
            name="Claude",
            client_id="workspace-refusal-test-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        cls.CONNECTION = MCPConnection.objects.create(
            user=cls.USER_VIEWER, application=cls.APPLICATION, tools=all_tool_names()
        )
        cls.CONNECTION.workspaces.set([cls.WORKSPACE])

    def setUp(self):
        super().setUp()
        self.mcp_user = MCPUser.from_user(self.USER_VIEWER, self.CONNECTION)


class WorkspaceRefusalTest(WorkspaceRefusalFixtures):
    def assertRefused(self, tool_name, arguments, slug):
        with self.assertRaises(PermissionDenied) as refusal:
            call_tool(tool_name, arguments, self.mcp_user, self.CONNECTION)
        message = str(refusal.exception)
        self.assertIn(f'not authorized to access workspace "{slug}"', message)
        self.assertIn("/user/account#mcp-connections", message)
        return message

    def test_an_ungranted_workspace_is_refused(self):
        slug = self.UNGRANTED_WORKSPACE.slug

        self.assertRefused("list_datasets", {"workspace_slug": slug}, slug)

    def test_a_guessed_slug_is_refused(self):
        self.assertRefused(
            "list_datasets", {"workspace_slug": "moreworkspace1"}, "moreworkspace1"
        )

    def test_a_write_to_an_ungranted_workspace_is_refused(self):
        slug = self.UNGRANTED_WORKSPACE.slug

        self.assertRefused(
            "create_dataset",
            {"workspace_slug": slug, "name": "Sneaky", "files_json": "[]"},
            slug,
        )

    def test_the_workspace_tools_are_refused_by_slug(self):
        slug = self.UNGRANTED_WORKSPACE.slug

        self.assertRefused("get_workspace", {"slug": slug}, slug)
        self.assertRefused("update_workspace", {"slug": slug, "name": "X"}, slug)

    def test_the_refusal_is_recorded(self):
        message = self.assertRefused(
            "list_datasets", {"workspace_slug": "moreworkspace1"}, "moreworkspace1"
        )

        call = ToolCall.objects.get(tool_name="list_datasets")
        self.assertFalse(call.success)
        self.assertEqual(message, call.error)

    def test_the_refusal_reaches_the_client_over_jsonrpc(self):
        response = handle_jsonrpc(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "list_datasets",
                        "arguments": {"workspace_slug": "moreworkspace1"},
                    },
                }
            ).encode(),
            self.mcp_user,
        )

        self.assertTrue(response["result"]["isError"])
        text = response["result"]["content"][0]["text"]
        self.assertIn('not authorized to access workspace "moreworkspace1"', text)

    def test_a_granted_workspace_is_not_refused(self):
        result = call_tool(
            "list_datasets",
            {"workspace_slug": self.WORKSPACE.slug},
            self.mcp_user,
            self.CONNECTION,
        )

        self.assertIn("datasets", result)

    def test_a_workspace_granted_through_its_organization_is_not_refused(self):
        self.CONNECTION.workspaces.clear()
        self.CONNECTION.organizations.add(self.WORKSPACE.organization)
        mcp_user = MCPUser.from_user(self.USER_VIEWER, self.CONNECTION)

        result = call_tool(
            "list_datasets",
            {"workspace_slug": self.WORKSPACE.slug},
            mcp_user,
            self.CONNECTION,
        )

        self.assertIn("datasets", result)

    def test_a_disabled_tool_is_refused_before_the_workspace(self):
        self.CONNECTION.tools = ["list_files"]
        self.CONNECTION.save()

        with self.assertRaises(PermissionDenied) as refusal:
            call_tool(
                "list_datasets",
                {"workspace_slug": "moreworkspace1"},
                self.mcp_user,
                self.CONNECTION,
            )

        self.assertIn("not authorized to call list_datasets", str(refusal.exception))


class UngrantedWorkspaceSearchTest(WorkspaceRefusalFixtures):
    def list_workspaces(self, **arguments):
        return call_tool("list_workspaces", arguments, self.mcp_user, self.CONNECTION)

    def test_a_search_matching_only_an_ungranted_workspace_says_so(self):
        result = self.list_workspaces(query="more")

        self.assertEqual([], result["workspaces"]["items"])
        self.assertIn(
            "not authorized to access the workspaces matching this search",
            result["message"],
        )

    def test_a_search_matching_nothing_has_no_message(self):
        result = self.list_workspaces(query="nothing-like-this")

        self.assertEqual([], result["workspaces"]["items"])
        self.assertNotIn("message", result)

    def test_a_search_matching_a_granted_workspace_has_no_message(self):
        result = self.list_workspaces(query="test")

        self.assertEqual(1, result["workspaces"]["totalItems"])
        self.assertNotIn("message", result)

    def test_a_workspace_the_person_cannot_access_is_not_hinted(self):
        create_workspace(self.USER_ADMIN, name="Hidden program")

        self.assertNotIn("message", self.list_workspaces(query="hidden"))


class WorkspaceArgumentConventionTest(SimpleTestCase):
    """call_tool finds a call's workspace by argument name; this keeps the tools to it."""

    def test_only_workspace_tools_take_a_bare_slug(self):
        for name, entry in _TOOLS.items():
            params = inspect.signature(entry.func).parameters
            with self.subTest(tool=name):
                if entry.resource == MCPResource.WORKSPACES:
                    self.assertNotIn("workspace_slug", params)
                else:
                    self.assertNotIn("slug", params)
