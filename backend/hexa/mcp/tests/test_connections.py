from hexa.mcp.tools.connections import list_connections

from .testutils import MCPTestCase


class ListConnectionsTest(MCPTestCase):
    def test_list_connections(self):
        result = list_connections(
            user=self.USER_ADMIN, workspace_slug=self.WORKSPACE.slug
        )
        connections = result["connections"]
        self.assertEqual(len(connections), 1)
        self.assertEqual(connections[0]["name"], "Test Connection")
        self.assertEqual(connections[0]["slug"], "test-connection")
        self.assertEqual(connections[0]["type"], "CUSTOM")

    def test_list_connections_workspace_not_found(self):
        result = list_connections(user=self.USER_ADMIN, workspace_slug="nonexistent")
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_list_connections_no_access(self):
        result = list_connections(
            user=self.USER_OUTSIDER, workspace_slug=self.WORKSPACE.slug
        )
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_list_connections_viewer(self):
        result = list_connections(
            user=self.USER_VIEWER, workspace_slug=self.WORKSPACE.slug
        )
        self.assertEqual(len(result["connections"]), 1)
